import json, hashlib, re, sys, xml.etree.ElementTree as ET
from pathlib import Path

BASE=Path(__file__).resolve().parent
INPUT=BASE/"book_benchmark/input"
OUT=BASE/"evidence/book_ingestion"
OUT.mkdir(parents=True,exist_ok=True)

SUPPORTED={".txt",".fb2",".pdf"}

def sha256_file(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def detect_text_encoding(data):
    for enc in ("utf-8-sig","utf-8","cp1251","windows-1251","koi8-r","latin-1"):
        try:
            return enc,data.decode(enc)
        except Exception:
            pass
    return "unknown",data.decode("utf-8",errors="replace")

def lang_guess(text):
    sample=text[:20000].lower()
    cyr=sum("а"<=c<="я" or c=="ё" for c in sample)
    lat=sum("a"<=c<="z" for c in sample)
    if cyr>lat*2 and cyr>50: return "ru"
    if lat>cyr*2 and lat>50: return "en_or_latin"
    return "mixed_or_unknown"

def split_chunks(text,source_file,fmt,language,chapter=None,page=None,size=4500,overlap=300):
    out=[]; i=0
    clean=text.replace("\r\n","\n").replace("\r","\n")
    while i<len(clean):
        part=clean[i:i+size]
        cid=f"{Path(source_file).stem}-{len(out)+1:05d}"
        out.append({
          "chunk_id":cid,
          "source_file":source_file,
          "format":fmt,
          "language":language,
          "chapter":chapter,
          "page":page,
          "char_start":i,
          "char_end":i+len(part),
          "text_original":part,
          "translation":None
        })
        if i+size>=len(clean): break
        i+=max(1,size-overlap)
    return out

def extract_txt(p):
    raw=p.read_bytes()
    enc,text=detect_text_encoding(raw)
    return {
      "format":"txt","encoding":enc,"language":lang_guess(text),
      "title":p.stem,"text":text,"sections":[],
      "media":[],"notes":[]
    }

def localname(tag):
    return tag.rsplit("}",1)[-1]

def node_text(node):
    return " ".join("".join(node.itertext()).split())

def extract_fb2(p):
    tree=ET.parse(p)
    root=tree.getroot()
    title=p.stem
    authors=[]
    language=None
    for e in root.iter():
        n=localname(e.tag)
        if n=="book-title" and (e.text or "").strip():
            title=(e.text or "").strip()
            break
    for e in root.iter():
        n=localname(e.tag)
        if n=="lang" and (e.text or "").strip():
            language=(e.text or "").strip()
            break
    for a in [x for x in root.iter() if localname(x.tag)=="author"]:
        parts=[]
        for c in list(a):
            if localname(c.tag) in {"first-name","middle-name","last-name"} and (c.text or "").strip():
                parts.append((c.text or "").strip())
        if parts: authors.append(" ".join(parts))
    sections=[]
    for idx,s in enumerate([x for x in root.iter() if localname(x.tag)=="section"],1):
        title_nodes=[x for x in list(s) if localname(x.tag)=="title"]
        stitle=node_text(title_nodes[0]) if title_nodes else f"section-{idx}"
        paras=[node_text(x) for x in s.iter() if localname(x.tag)=="p"]
        text="\n".join(x for x in paras if x)
        if text.strip(): sections.append({"title":stitle,"text":text})
    full="\n\n".join(x["text"] for x in sections)
    return {
      "format":"fb2","encoding":"utf-8/xml","language":language or lang_guess(full),
      "title":title,"authors":authors,"text":full,"sections":sections,
      "media":[],"notes":[]
    }

def extract_pdf(p):
    try:
        from pypdf import PdfReader
    except Exception as e:
        return {
          "format":"pdf","encoding":None,"language":"unknown","title":p.stem,
          "text":"","sections":[],"media":[],"notes":["PYPDF_NOT_INSTALLED: "+str(e)],
          "status":"DEPENDENCY_MISSING"
        }
    reader=PdfReader(str(p))
    pages=[]; full=[]
    for i,page in enumerate(reader.pages,1):
        try: text=page.extract_text() or ""
        except Exception as e: text=""; 
        pages.append({"page":i,"text":text})
        full.append(text)
    txt="\n\n".join(full)
    return {
      "format":"pdf","encoding":"embedded-text","language":lang_guess(txt),
      "title":(reader.metadata.title if reader.metadata and reader.metadata.title else p.stem),
      "text":txt,"sections":pages,"media":[],"notes":[],
      "pages":len(reader.pages),
      "status":"OK" if txt.strip() else "VISION_OCR_REQUIRED"
    }

def ingest(p):
    ext=p.suffix.lower()
    if ext==".txt": data=extract_txt(p)
    elif ext==".fb2": data=extract_fb2(p)
    elif ext==".pdf": data=extract_pdf(p)
    else: return None

    data.setdefault("status","OK")
    data["source_file"]=p.name
    data["source_path"]=str(p)
    data["source_hash"]=sha256_file(p)
    data["source_bytes"]=p.stat().st_size

    chunks=[]
    if data["format"]=="fb2" and data.get("sections"):
        for s in data["sections"]:
            chunks.extend(split_chunks(s.get("text",""),p.name,"fb2",data["language"],chapter=s.get("title")))
    elif data["format"]=="pdf" and data.get("sections"):
        for s in data["sections"]:
            chunks.extend(split_chunks(s.get("text",""),p.name,"pdf",data["language"],page=s.get("page")))
    else:
        chunks=split_chunks(data.get("text",""),p.name,data["format"],data["language"])

    data["chunk_count"]=len(chunks)
    data["text_chars"]=len(data.get("text",""))
    return data,chunks

def main():
    INPUT.mkdir(parents=True,exist_ok=True)
    files=[p for p in sorted(INPUT.iterdir()) if p.is_file() and p.suffix.lower() in SUPPORTED]
    print("=== FATHER BOOK INGESTION MVP-01 ===",flush=True)
    print("INPUT:",INPUT,flush=True)
    print("FILES:",len(files),flush=True)
    if not files:
        print("RESULT: FAIL - no supported books",flush=True)
        return 2

    manifest=[]
    all_chunks=[]
    ok=True

    for p in files:
        print(f"\nREAD {p.name}",flush=True)
        try:
            data,chunks=ingest(p)
            manifest.append(data)
            all_chunks.extend(chunks)
            print(" FORMAT:",data["format"],flush=True)
            print(" STATUS:",data["status"],flush=True)
            print(" LANGUAGE:",data["language"],flush=True)
            print(" CHARS:",data["text_chars"],flush=True)
            print(" CHUNKS:",data["chunk_count"],flush=True)
            if data["status"] not in {"OK","VISION_OCR_REQUIRED"}:
                ok=False
        except Exception as e:
            ok=False
            manifest.append({"source_file":p.name,"status":"ERROR","error":type(e).__name__+": "+str(e)})
            print(" ERROR:",type(e).__name__,e,flush=True)

    canonical={
      "schema":"FATHER_CANONICAL_BOOK_COLLECTION_v1",
      "books":manifest
    }
    (OUT/"canonical_books.json").write_text(json.dumps(canonical,ensure_ascii=False,indent=2),encoding="utf-8")
    with (OUT/"chunks.jsonl").open("w",encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c,ensure_ascii=False)+"\n")

    summary={
      "books_total":len(files),
      "books_ingested":sum(1 for x in manifest if x.get("status") in {"OK","VISION_OCR_REQUIRED"}),
      "chunks_total":len(all_chunks),
      "formats":sorted({x.get("format") for x in manifest if x.get("format")}),
      "languages":sorted({x.get("language") for x in manifest if x.get("language")}),
      "books":[{"file":x.get("source_file"),"format":x.get("format"),"status":x.get("status"),"language":x.get("language"),"chars":x.get("text_chars"),"chunks":x.get("chunk_count"),"notes":x.get("notes",[])} for x in manifest]
    }
    (OUT/"extraction_report.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")

    print("\nSUMMARY:",json.dumps(summary,ensure_ascii=False),flush=True)
    print("CANONICAL:",OUT/"canonical_books.json",flush=True)
    print("CHUNKS:",OUT/"chunks.jsonl",flush=True)
    print("REPORT:",OUT/"extraction_report.json",flush=True)
    print("RESULT:","PASS" if ok else "PARTIAL",flush=True)
    return 0 if ok else 1

if __name__=="__main__":
    raise SystemExit(main())
