@echo off
python export.py
cd Result
for /R %%f in (*Pak.xml) do (
    @echo ..\Metawrite\Metawrite.exe --protocol ..\Metawrite\protocol.xml --in %%f --out %%~df%%~pf%%~nf.bin
    ..\Metawrite\Metawrite.exe --protocol ..\Metawrite\protocol.xml --in %%f --out %%~df%%~pf%%~nf.bin
    del %%f
)
cd ..
python paks2zip.py
