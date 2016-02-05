python setup.py py2exe -b 1
mkdir ..\..\whichwayisup_build_bin\
move dist\* ..\..\whichwayisup_build_bin\
cd ..
cd ..
copy "whichwayisup\README.txt" whichwayisup_build_bin\
copy "whichwayisup\changelog.txt" whichwayisup_build_bin\
mkdir whichwayisup_build_bin\data\
mkdir whichwayisup_build_bin\data\pictures\
mkdir whichwayisup_build_bin\data\sounds\
mkdir whichwayisup_build_bin\data\music\
mkdir whichwayisup_build_bin\data\misc\
mkdir whichwayisup_build_bin\data\levels\
copy whichwayisup\data\pictures\* whichwayisup_build_bin\data\pictures\
copy whichwayisup\data\sounds\* whichwayisup_build_bin\data\sounds\
copy whichwayisup\data\music\* whichwayisup_build_bin\data\music\
copy whichwayisup\data\misc\* whichwayisup_build_bin\data\misc\
copy whichwayisup\data\levels\* whichwayisup_build_bin\data\levels\
cd whichwayisup
cd lib
del /Q *.pyc
del /Q build\*
rmdir /S /Q build
rmdir /S /Q dist
