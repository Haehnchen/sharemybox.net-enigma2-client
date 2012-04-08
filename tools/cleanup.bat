@echo off
    for /R "." %%f in (*.pyc) do (
    del %%f
)

@echo off
    for /R "." %%f in (*.pyo) do (
    del %%f
)
