# 전체 폴더 구조
```
root/
├── converterCLI/
│   ├── .gitignore
│   ├── HwpxConverterCLI.class
│   ├── HwpxConverterCLI.java
│   ├── py_hwpx_converter.py
│   └── readme.md
├── hwp_server/
│   ├── hwp2hwpx/
│   ├── hwplib/
│   ├── hwpxlib/
│   ├── src/
│   ├── target/
│   ├── .gitignore
│   ├── ConvertMain.class
│   ├── ConvertMain.java
│   ├── pom.xml
│   └── readme.md
├── py_converter.py
└── setup_hwpx.py
```

# 설치해야 되는 부가 라이브러리 (순서에 맞춰서 설치)
1. hwplib<br>
- https://github.com/qazcdek/hwplibjdk<br>
버전 1.8 이상에 맞게 수정
2. hwpxlib<br>
- https://github.com/qazcdek/hwpxlib<br>
jdk 버전 1.8 이상<br>
표 병합셀은 병합된 모든 자리에 같은 내용으로 복사<br>
각 행 시작과 끝에도 seperator("|")를 붙여서 llm이 표 구조로 인식하기 쉽게 변경<br>
표 캡션의 경우 위에 있으면 [표 제목], 밑에 있으면 [표 설명] 이라는 prefix를 추가하고 표 바로 윗줄에 캡션 추출<br>
3. hwp2hwpx<br>
- https://github.com/qazcdek/hwp2hwpx<br>
jdk 버전 1.8 이상<br>
4. hwp_server(optional)
- https://github.com/qazcdek/hwp_server<br>
api 형태로 hwp파일을 업로드하고 파싱된 결과를 받을 수 있는 서버
5. cli 버전<br>
- https://github.com/qazcdek/hwp_converter_cli<br>
실행 가능한 버전으로 만듬.

# 현재 setup_hwpx.py 역할
- 위 모든 라이브러리를 정해진 경로에 다운받으면, 모든 라이브러리를 일괄 설치.