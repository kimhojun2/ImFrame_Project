#include <Wire.h>  // I2C 통신을 위한 Wire 라이브러리를 포함합니다.
#include <eloquent.h>  // Eloquent Arduino 라이브러리를 포함합니다.
#include <eloquent/collections/circular_buffer.h>  // 순환 버퍼를 위한 라이브러리를 포함합니다.
#include <eloquent/modules/vl53l5cx/8x8.h>  // VL53L5CX 센서를 위한 라이브러리를 포함합니다.

// Edge Impulse에서 다운로드 받은 라이브러리로 교체하세요.
#include <eloquent/tinyml/edgeimpulse.h>  // Edge Impulse 머신러닝 기능을 위한 라이브러리를 포함합니다.
#include <eloquent/tinyml/voting/quorum.h>  // 의사 결정 투표 시스템을 위한 라이브러리를 포함합니다.
#include <smartthings-project-1_inferencing.h>

Eloquent::Collections::FloatCircularBuffer<EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE>
    buffer;  // 입력 데이터를 저장할 순환 버퍼를 생성합니다.
Eloquent::TinyML::EdgeImpulse::Impulse impulse(
    false);  // Edge Impulse 추론 객체를 생성합니다.
// 투표 수를 원하는 값으로 변경하세요. 높은 값은 예측을 덜 잡음이 많게 하지만,
// 반응성을 떨어뜨릴 수 있습니다.
Eloquent::TinyML::Voting::Quorum<7> voting;

void setup() {
  Serial.begin(115200);  // 시리얼 통신을 115200 baud로 시작합니다.
  Wire.begin();          // I2C 통신을 초기화합니다.
  Wire.setClock(1000000);  // I2C 클록 속도를 1MHz로 설정합니다.

  vllcx.highFreq();  // VL53L5CX 센서를 고주파 모드로 설정합니다.
  vllcx.truncateLowerThan(150);  // 150mm보다 낮은 측정값을 무시합니다.
  vllcx.truncateHigherThan(400);  // 400mm보다 높은 측정값을 무시합니다.
  vllcx.scaleToRange(0, 1);  // 측정값을 0과 1 사이로 스케일합니다.

  // N개의 최근 예측 중 절반 이상이 일치할 때 잡음이 없는 것으로 간주합니다.
  voting.atLeastMajority();

  if (!vllcx.begin())  // VL53L5CX 센서를 시작합니다.
    eloquent::abort(
        Serial, "vl53l5cx not found");  // 센서를 찾지 못하면 실행을 중지하고
                                        // 오류 메시지를 출력합니다.

  Serial.println("vl53l5cx is ok");  // 센서가 정상적으로 작동하는지 확인
                                     // 메시지를 출력합니다.
  Serial.println("Start collecting data...");  // 데이터 수집을 시작한다는
                                               // 메시지를 출력합니다.
}

void loop() {
  if (!vllcx.hasNewData() || !vllcx.read() || vllcx.mean() > 0.98)
    // 데이터가 준비되었거나 객체가 시야에 들어올 때까지 기다립니다.
    return;

  if (!buffer.push(vllcx.distances, 64))
    // 큐가 가득 차지 않았다면 반환합니다.
    return;

  // 제스처를 분류할 준비가 되었습니다.
  uint8_t prediction = impulse.predict(buffer.values);

  if (impulse.getProba() < 0.9)
    // (선택 사항) 약한 예측을 버립니다.
    return;

  if (voting.vote(prediction) < 0)
    // 예측이 잡음이 많다면 반환합니다.
    return;

  Serial.print("Predicted label: ");
  Serial.print(impulse.getLabel());
  Serial.print(" with probability ");
  Serial.println(impulse.getProba());

  // 디버그 클래스 확률과 타이밍
  // impulse.printTo(Serial);
}
