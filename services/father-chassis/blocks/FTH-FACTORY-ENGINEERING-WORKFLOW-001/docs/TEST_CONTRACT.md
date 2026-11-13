# Test Contract
Owner: Senior Test Architect.

Acceptance:
AC-WF-01 approved external request persists.
AC-WF-02 completed stage persists across restart.
AC-WF-03 next stage is identical after restart.
AC-WF-04 history persists.
AC-WF-05 different workflow_id is isolated.
AC-WF-06 tampered artifact hash fails restore.
AC-WF-07 wrong role remains blocked.
AC-WF-08 developer-before-DevelopmentPacket remains blocked after restore.
AC-WF-09 existing no-store behavior remains compatible.

Qualification:
full regression PASS + dedicated restart lifecycle PASS.

No hard latency SLO yet; state operations must remain negligible versus LLM execution, to be measured later.