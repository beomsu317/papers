# PDF 논문 한글 번역 가이드

> **번역 안내:**
> - 한글 번역 시 대부분의 IT/AI/논문 전문 용어(예: Transformer, attention, model, layer, encoder, decoder, self-attention, feed-forward, embedding, softmax, BLEU 등)는 영어로 그대로 표기합니다.
> - 문장 구조와 설명은 자연스러운 한글로 번역하되, **논문 제목, 모든 소제목(heading), figure/table의 caption(설명문)은 영어로 유지**합니다.
> - 논문 번역 시 반드시 원문의 항목(섹션, 소제목, 본문 등) 순서를 그대로 유지해야 합니다. (예: Abstract → 1 Introduction → 2 Background → ... → References)
> - 본문에 등장하는 모든 수식은 GitHub LaTeX(인라인: `$...$`, 블록: `$$...$$`) 형태로 작성합니다.
> - **참고문헌(References)은 반드시 영어 원문 그대로 포함해야 하며, 절대 생략하지 말고 모두 번역 결과에 포함해야 합니다.**

## 📚 단계별 상세 가이드

### 1. PDF 파일 경로 확인
- 번역할 PDF 파일의 전체 경로를 확인합니다. (예: `/Users/user/Desktop/papers/attention-is-all-you-need/1706.03762v7.pdf`)

### 2. PDF 텍스트 추출, 번역, 자동 디렉토리 및 파일 저장
- 아래 프롬프트에서 `<PDF_FILE_PATH>`를 실제 경로로 바꿔 입력합니다.
  ```
  <PDF_FILE_PATH>에 있는 논문을 한글로 번역해줘. 논문 제목, 모든 소제목(heading), figure/table의 caption(설명문)은 영어로 유지하고, 본문 내용만 자연스러운 한글로 번역해줘. 논문 제목으로 디렉토리를 만들고, 번역 결과는 그 디렉토리의 README.md 파일로 자동 저장해줘. 단, 번역 시 대부분의 IT/AI/논문 전문 용어(예: Transformer, attention, model, layer, encoder, decoder, self-attention, feed-forward, embedding, softmax, BLEU 등)는 영어 그대로 사용하고, 본문에 등장하는 모든 수식은 GitHub LaTeX(인라인: `$...$`, 블록: `$$...$$`) 형태로 작성해줘. 참고문헌은 영어 원문 그대로 반드시 모두 번역 결과에 포함해줘.
  ```
  - **이미지(figure)와 표(table)는 번역 및 결과물에 포함하지 않고 모두 무시합니다.**
    - 논문 내 등장하는 모든 figure(이미지)와 table(표)는 번역 과정에서 생략합니다.

  
  **마지막 단계 체크리스트:**
    - 번역이 끝난 후, 본문과 참고문헌 뒤에 추가 데이터(appendix 등)가 누락되지 않았는지 반드시 확인합니다.
    - 참고문헌(References)은 영어 원문 그대로 반드시 모두 번역 결과에 포함해야 하며, 절대 생략하지 말아야 합니다.
    - 누락된 데이터가 있다면 모두 번역 결과에 포함합니다.

### 3. 논문 제목 추출 및 디렉토리 생성
```  
  <PDF_FILE_PATH> 파일의 제목을 추출해줘.
  "추출된 제목"으로 디렉토리를 만들어줘. 공백은 하이픈으로 바꾸고 모두 소문자로 만들어줘.
  ```

### 4. 전문 용어 유지 번역
- 번역 시 특정 용어를 영어로 남기고 싶을 때는 아래와 같이 요청합니다.
  ```
  <PDF_FILE_PATH>에 있는 논문을 한글로 번역해줘. 논문 제목, 모든 소제목(heading), figure/table의 caption(설명문)은 영어로 유지하고, 본문 내용만 자연스러운 한글로 번역해줘. 논문 제목으로 디렉토리를 만들고, 번역 결과는 그 디렉토리의 README.md 파일로 자동 저장해줘. 단, 번역 시 대부분의 IT/AI/논문 전문 용어(예: Transformer, attention, model, layer, encoder, decoder, self-attention, feed-forward, embedding, softmax, BLEU 등)는 영어 그대로 사용해줘. 참고문헌은 영어 원문 그대로 반드시 모두 번역 결과에 포함해줘.
  ```

### 5. 참고문헌 처리 안내
- 본문 내 참고문헌 인용 번호는 `[1]`, `[2]`와 같이, 단순한 숫자 대괄호 형태로 표기합니다.
  - 예시 (본문): `이 방법은 기존 연구[1]와 비교하여 ...`
- 하단 참고문헌 항목은 반드시 마크다운 리스트(- 또는 *) 형태로 작성하며, 각 번호별로 번호만 표기합니다.
  - 예시 (하단): `- [1] Lei Ba et al. Layer normalization.`
  - 마크다운 리스트 예시:
    ```markdown
    - [1] Lei Ba et al. Layer normalization.
    - [2] Vaswani et al. Attention is all you need.
    ```
- 각 참고문헌 항목은 논문 제목을 영어 원문 그대로 표기합니다.
  - 참고문헌 번호는 본문 내 인용([1], [2], ...)과 일치해야 하며, 번호는 그대로 사용합니다.

---
**전체 논문 번역 예시 (Best Practice)**

```markdown
# Attention Is All You Need

## Abstract
We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.

우리는 attention 메커니즘만을 기반으로 하는 새로운 간단한 네트워크 아키텍처인 Transformer를 제안한다. 이 구조는 recurrence와 convolution을 완전히 배제한다.

## 1 Introduction
The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder.

기존의 시퀀스 변환 모델은 encoder와 decoder를 포함하는 복잡한 recurrent 또는 convolutional neural network에 기반한다.

The Transformer, a model architecture eschewing recurrence and instead relying entirely on an attention mechanism to draw global dependencies between input and output.

Transformer는 recurrence를 사용하지 않고 attention 메커니즘만으로 입력과 출력 간의 전역적 의존성을 학습한다.

## 2 Background
Attention mechanisms have become an integral part of compelling sequence modeling and transduction models in various tasks.

Attention 메커니즘은 다양한 작업에서 시퀀스 모델링 및 변환 모델의 핵심 요소가 되었다.

### 2.1 Notation and Definitions
Given a sequence of inputs $x = (x_1, ..., x_n)$, the output is computed as follows:

입력 시퀀스 $x = (x_1, ..., x_n)$에 대해 출력은 다음과 같이 계산된다:

$$
y_i = \text{Transformer}(x_1, ..., x_n)
$$

## References
- [1] Vaswani, A., Shazeer, N., Parmar, N., et al. Attention is all you need.
- [2] Bahdanau, D., Cho, K., Bengio, Y. Neural machine translation by jointly learning to align and translate.
```

---
- 위 예시는 실제 논문 일부를 발췌해 번역, 수식, 참고문헌까지 포함한 전체 결과물의 형태를 보여줍니다.
- 표, 그림 등은 포함하지 않습니다.
- 실제 번역 시 논문 전체를 위와 같은 형식으로 작성하면 됩니다.
---