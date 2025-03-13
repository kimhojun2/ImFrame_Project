#include <Wire.h>  // I2C 통신을 위한 Wire 라이브러리를 포함합니다.
#include <eloquent.h>  // 하드웨어와의 인터페이스를 단순화하는 Eloquent Arduino 라이브러리를 포함합니다.
#include <eloquent/modules/vl53l5cx/8x8.h>  // VL53L5CX 센서를 위한 특정 라이브러리를 포함합니다.

void setup() {
  Serial.begin(
      115200);  // 디버깅을 위해 115200 보드레이트로 시리얼 통신을 시작합니다.
  Wire.begin();            // I2C 통신을 초기화합니다.
  Wire.setClock(1000000);  // I2C 클록 속도를 1MHz로 설정합니다.

  vllcx.highFreq();  // VL53L5CX 센서를 고주파 모드로 설정합니다.
  vllcx.truncateLowerThan(150);  // 30mm보다 낮은 모든 측정을 무시합니다.
  vllcx.truncateHigherThan(400);  // 200mm보다 높은 모든 측정을 무시합니다.
  vllcx.scaleToRange(0, 1);  // 거리 측정을 0에서 1의 범위로 스케일합니다.

  if (!vllcx.begin())  // VL53L5CX 센서를 시작합니다.
    eloquent::abort(Serial,
                    "vl53l5cx not found");  // 센서를 찾지 못하면 실행을
                                            // 중지하고 오류를 출력합니다.

  Serial.println("vl53l5cx is ok");  // 센서가 발견되고 초기화되면 성공 메시지를
                                     // 출력합니다.
  Serial.println(
      "Start collecting data...");  // 데이터 수집이 시작될 것임을 알립니다.
  delay(3000);  // 주요 루프를 시작하기 전에 3초 동안 대기합니다.
}

void loop() {
  if (!vllcx.hasNewData() ||
      !vllcx.read())  // 새로운 데이터가 있는지 확인하고 읽습니다.
    return;  // 새 데이터가 없으면 루프 반복을 종료하고 다시 확인합니다.

  if (vllcx.mean() >
      0.98)  // 평균 측정값이 0.98(1에 가까운 최대 범위) 이상인지 확인합니다.
    return;  // 객체가 최대 범위에 너무 가까우면 처리를 건너뜁니다.

  vllcx.printTo(Serial);  // 시리얼 포트로 센서 데이터를 출력하여 디버깅 및
                          // 모니터링을 합니다.
}
