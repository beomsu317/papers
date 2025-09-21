

# PDF 논문 한글 번역 가이드 (업데이트)

**LLM 번역 안내 및 품질 기준:**
- 논문 제목, 모든 소제목(heading), figure/table의 caption(설명문)은 영어로 남기고, 본문은 자연스러운 한글로 번역합니다.
- 주요 IT/AI 용어(예: Transformer, attention, model, layer, encoder, decoder, self-attention, feed-forward, embedding, softmax, BLEU 등)는 영어로 표기합니다.
- 논문 원문의 항목(섹션, 소제목, 본문 등) 순서를 반드시 그대로 유지합니다. (예: Abstract → 1 Introduction → 2 Background → ... → References)
- 본문에 등장하는 모든 수식은 GitHub LaTeX(인라인: `$...$`, 블록: `$$...$$`) 형태로 작성합니다.
- 그림(figure)과 표(table)는 번역 및 결과물에 포함하지 않고 모두 무시합니다.
- 참고문헌(References)은 영어 원문 그대로 모두 포함하고, 절대 생략하지 않습니다.
- 번역이 어색하거나 직역이 자연스럽지 않은 경우, 의미가 잘 전달되도록 자연스러운 한글로 의역합니다.
- 논문 내 figure/table 번호, caption, 수식 번호 등은 영어 원문 그대로 남깁니다.
- 논문 전체 구조(섹션, 소제목, 본문, 참고문헌, appendix 등)가 누락 없이 모두 포함되어야 합니다.
- 번역이 어려운 용어나 문장은 주석(<!-- ... -->)으로 원문을 함께 남겨도 좋습니다.

## 단계별 상세 가이드

### 1. PDF 파일 경로 확인
- 번역할 PDF 파일의 전체 경로를 확인합니다. (예: `/Users/user/Desktop/papers/attention-is-all-you-need/1706.03762v7.pdf`)

### 2. LLM 번역 프롬프트 (예시)
- 아래 프롬프트에서 `<PDF_FILE_PATH>`와 `<OUTPUT_FILE_NAME>`을 실제 경로와 파일명으로 바꿔 입력합니다.

```
너는 AI 분야의 학술 논문을 전문적으로 번역하는 번역가야.

# 작업
<PDF_FILE_PATH> 경로의 논문을 아래 규칙에 따라 한글로 번역해서 <OUTPUT_FILE_NAME>.md 파일로 만들어줘.

# 번역 규칙
1. **유지 항목**: 논문 제목, 모든 소제목(heading), figure/table의 caption은 번역하지 말고 영어 원문 그대로 유지해줘.
2. **주요 용어**: 아래 목록의 IT/AI 용어는 번역하지 말고 영어로 표기해줘.
   - Transformer, attention, model, layer, encoder, decoder, self-attention, multi-head attention, feed-forward, embedding, softmax, positional encoding, BLEU, ROUGE, LLM, NLP, NLU, NLG
3. **번역 스타일**: 본문은 전문적인 학술 톤을 유지하면서도, 독자가 이해하기 쉽도록 자연스러운 한글로 번역해줘. 직역이 어색할 경우 의미를 살려 의역해줘.
4. **수식**: 본문의 모든 수식은 GitHub LaTeX 형식(인라인: `$ ... $`, 블록: `$$ ... $$`)으로 정확하게 작성해줘.
5. **참고문헌**:
   - 본문 내 인용은 `[1]`, `[2, 3]`, `[4-7]`과 같이 대괄호 안에 숫자로 표기해줘.
   - 문서 마지막의 참고문헌(References) 섹션은 영어 원문 그대로 모두 포함하고, 각 항목은 마크다운 리스트(- 또는 *)로 작성해줘. (예: `- [1] Author, A. et al. ...`)
6. **제외 항목**: 그림(figure)과 표(table)의 내용 자체는 결과물에 포함하지 말고 무시해줘.
7. **구조 유지**: Abstract, Introduction, ..., Conclusion, References, Appendix 등 논문 원문의 전체 구조와 순서를 반드시 유지해줘. 누락되는 섹션이 없도록 꼼꼼히 확인해줘.
8. **주석 활용**: 번역이 어렵거나 의미가 모호한 문장은 원문을 HTML 주석 `<!-- 원문: ... -->` 형태로 함께 남겨줘도 좋아.

# 출력 형식
- 전체 번역 내용은 마크다운 형식으로 작성해줘.
- 파일 최상단에는 논문 제목을 `#`을 사용해 가장 큰 제목으로 표기해줘.
```

### 3. (사용자 정의 단계)
*이 단계는 필요에 따라 추가 내용을 작성하거나, 프로젝트별 안내를 삽입할 수 있습니다.*

**마지막 단계 체크리스트:**
- 번역이 끝난 후, 본문과 참고문헌 뒤에 appendix 등 추가 데이터가 누락되지 않았는지 반드시 확인합니다.
- 참고문헌(References)은 영어 원문 그대로 반드시 모두 번역 결과에 포함해야 하며, 절대 생략하지 말아야 합니다.
- 누락된 데이터가 있다면 모두 번역 결과에 포함합니다.

### 4. 전문 용어 유지 번역
- 기본 규칙 외에 특정 용어를 영어로 남기고 싶을 때는 아래처럼 `추가 용어` 목록에 추가하여 요청하세요.

```
너는 AI 분야의 학술 논문을 전문적으로 번역하는 번역가야.

# 작업
<PDF_FILE_PATH> 경로의 논문을 아래 규칙에 따라 한글로 번역해서 <OUTPUT_FILE_NAME>.md 파일로 만들어줘.

# 번역 규칙
1. **유지 항목**: 논문 제목, 모든 소제목(heading), figure/table의 caption은 번역하지 말고 영어 원문 그대로 유지해줘.
2. **주요 용어**: 아래 목록의 IT/AI 용어는 번역하지 말고 영어로 표기해줘.
   - **기본 용어**: Transformer, attention, model, layer, encoder, decoder, self-attention, multi-head attention, feed-forward, embedding, softmax, positional encoding, BLEU, ROUGE, LLM, NLP, NLU, NLG
   - **추가 용어**: [ 여기에 "추가하고 싶은 용어1", "용어2" 등을 입력하세요 ]
3. **번역 스타일**: 본문은 전문적인 학술 톤을 유지하면서도, 독자가 이해하기 쉽도록 자연스러운 한글로 번역해줘. 직역이 어색할 경우 의미를 살려 의역해줘.
4. **수식**: 본문의 모든 수식은 GitHub LaTeX 형식(인라인: `$ ... $`, 블록: `$$ ... $$`)으로 정확하게 작성해줘.
5. **참고문헌**:
   - 본문 내 인용은 `[1]`, `[2, 3]`, `[4-7]`과 같이 대괄호 안에 숫자로 표기해줘.
   - 문서 마지막의 참고문헌(References) 섹션은 영어 원문 그대로 모두 포함하고, 각 항목은 마크다운 리스트(- 또는 *)로 작성해줘. (예: `- [1] Author, A. et al. ...`)
6. **제외 항목**: 그림(figure)과 표(table)의 내용 자체는 결과물에 포함하지 말고 무시해줘.
7. **구조 유지**: Abstract, Introduction, ..., Conclusion, References, Appendix 등 논문 원문의 전체 구조와 순서를 반드시 유지해줘. 누락되는 섹션이 없도록 꼼꼼히 확인해줘.
8. **주석 활용**: 번역이 어렵거나 의미가 모호한 문장은 원문을 HTML 주석 `<!-- 원문: ... -->` 형태로 함께 남겨줘도 좋아.

# 출력 형식
- 전체 번역 내용은 마크다운 형식으로 작성해줘.
- 파일 최상단에는 논문 제목을 `#`을 사용해 가장 큰 제목으로 표기해줘.
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