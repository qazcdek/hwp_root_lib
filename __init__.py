import logging

# # 로거 객체 가져오기
# service_logger = logging.getLogger("ai_agent")

# 로거 객체
java_logger = logging.getLogger("java")
java_logger.setLevel(logging.INFO)# 테스트 시작

# 콘솔 핸들러
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 파일 핸들러
file_handler = logging.FileHandler("logs/java.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)

# 포맷터
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 핸들러 등록 (중복 방지)
if not java_logger.handlers:
    java_logger.addHandler(console_handler)
    java_logger.addHandler(file_handler) # 테스트 마침

# Add this test right here:
java_logger.info("LOGGING CONFIG TEST - This should appear in both console and file")
print("Regular print statement for comparison")