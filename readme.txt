收集虚拟环境依赖库：
pip freeze > requirements.txt

打包不同平台image
docker buildx build --platform linux/amd64,linux/arm64/v8,linux/arm/v7 -t elthamliudocker/wiser_zigbee_launcher --push .
docker buildx build --platform linux/arm64/v8,linux/arm/v7 -t elthamliudocker/wiser_zigbee_launcher --push .

打包成windows exe文件：
pyinstaller -F -p D:\projects\zigbee_launcher\development\venv\Lib\site-packages -w -i logo.ico --version-file version_file.txt launcher.py