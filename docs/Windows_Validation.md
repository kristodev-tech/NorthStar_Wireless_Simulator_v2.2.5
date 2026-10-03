# Windows verification

The application has automated source checks and a frozen startup self-check. These are useful, but testing Linux does not validate Windows fonts, scaling or installer behavior.

The included .github/workflows/windows-validation.yml runs on GitHub's Windows runners when this complete project is uploaded to the root of a repository. It checks Python 3.11, 3.12 and 3.13, and Qt scale factors 1, 1.25 and 1.5. The Python 3.12/scale 1 job also builds and checks the EXE and compiles the Inno Setup installer. Signing is not part of that workflow. GitHub must have Actions enabled; it has not been run from this workspace.

Local builds still use 01_Setup_Environment.bat followed by 04_Build_Exe.bat. The same checks run through scripts/quality_checks.py. They stop on failures and preserve build/quality_checks.log plus a JUnit report. A failed GUI test also saves a screenshot and widget/font/width information under build/diagnostics. Those files identify which control constrained the layout.

Before publishing an installer, run the Windows workflow and complete the visible UI and installed-app checks in Release_Checklist.md. A successful compiler exit does not prove every application workflow works on every device. Release checks reduce regressions; they cannot guarantee there will never be new errors.

## Build gates from 2.2.5

The normal quality runner excludes only tests marked `layout_stress`. Functional checks and original 1024×700/1366×768 layout checks remain required. The three extreme layout cases remain available through 07_Layout_Stress_Tests.bat and produce quality_checks_stress.log / pytest-stress-results.xml. CI runs them as a separate review step with continue-on-error, while normal checks and EXE/installer compilation remain blocking steps. The known stress-only Windows overflow has not been represented as fixed.
