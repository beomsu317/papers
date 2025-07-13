# HalluLens: LLM Hallucination Benchmark

Yejin Bang³,*, Ziwei Ji³,*, Alan Schelten², Anthony Hartshorn², Tara Fowler², Cheng Zhang², Nicola Cancedda¹, Pascale Fung ¹,³
¹FAIR at Meta, ²GenAI at Meta, ³HKUST
*Work done during Internship at FAIR

Large language models (LLMs)는 종종 사용자 입력이나 훈련 데이터에서 벗어난 응답을 생성하는데, 이를 "환각(hallucination)" 현상이라고 합니다. 이러한 환각은 사용자 신뢰를 저해하고 생성형 AI 시스템의 채택을 방해합니다. 환각을 해결하는 것은 LLM의 발전에 필수적입니다. 이 논문은 환각에 대한 명확한 분류 체계를 기반으로 새로운 외인성 및 기존 내재적 평가 작업을 통합한 포괄적인 환각 벤치마크를 소개합니다. 환각 벤치마킹의 주요 과제는 일관되지 않은 정의와 분류로 인한 통일된 프레임워크의 부재입니다. 우리는 LLM 환각을 "사실성(factuality)"과 분리하여 외인성 환각과 내재적 환각을 구별하는 명확한 분류 체계를 제안하여 일관성을 높이고 연구를 촉진하고자 합니다. 생성된 콘텐츠가 훈련 데이터와 일치하지 않는 외인성 환각은 LLM이 발전함에 따라 점점 더 중요해지고 있습니다. 우리 벤치마크는 데이터 유출을 완화하고 이러한 유출에 대한 견고성을 보장하기 위해 동적 테스트 세트 생성을 포함합니다. 또한 기존 벤치마크를 분석하여 그 한계와 포화 상태를 강조합니다. 이 연구의 목표는 다음과 같습니다: (1) 명확한 환각 분류 체계 수립, (2) 유출로 인한 포화를 방지하기 위해 동적으로 재생성할 수 있는 데이터로 새로운 외인성 환각 작업 도입, (3) 기존 벤치마크에 대한 포괄적인 분석을 제공하여 사실성 평가와 구별.

Date: April 25, 2025
Correspondence: yjbang@connect.ust.hk; pascalefung@meta.com
Code: https://github.com/facebookresearch/HalluLens

## 1 Introduction

Large language models (LLMs)는 사용자 입력, 자체 이전 출력 또는 기존 지식과 일치하지 않을 수 있는 응답을 생성하는 것으로 알려져 있으며, 이는 일반적으로 "환각(hallucination)"이라고 불리는 현상입니다. 이러한 환각은 특히 다운스트림 의사 결정에 영향을 미칠 때 사용자 신뢰와 생성 AI 시스템 수용에 상당한 어려움을 제기합니다. 따라서 환각을 식별하고 완화하는 것은 LLM의 광범위한 채택과 추가 개발에 중요합니다. 우리는 포괄적이고 신뢰할 수 있으며 조작하기 어려운 평가가 효과적인 완화를 향한 첫 번째 단계라고 믿습니다.

LLM의 환각을 벤치마킹하는 데 있어 주요 과제 중 하나는 다양한 유형과 원인에 대한 합의된 정의가 부족하여 포괄적인 평가를 위한 통일된 프레임워크가 없다는 점입니다. LLM 환각 평가를 위한 여러 벤치마크가 존재하지만(Li et al., 2024; Ming et al., 2024; Ji et al., 2024; Sun et al., 2024), 종종 고려되는 환각의 유형을 명시하지 않거나 범주가 서로 일치하지 않습니다. 이는 일관되지 않은 적용 범위와 연구 통찰력의 격차를 초래합니다. 더욱이 LLM이 발전함에 따라 LLM 환각은 종종 "사실성(factuality)"과 혼동됩니다(Wei et al., 2024a; Lin et al., 2022; Mallen et al., 2023b). "환각"과 "사실성"은 겹치지만, 별도의 벤치마크와 해결책을 필요로 하는 별개의 과제입니다(Wang et al., 2023; Augenstein et al., 2024). 특히, 사실성은 모델 또는 AI 시스템 외부의 오라클이 정답을 정의해야 합니다. 환각은 훈련 코퍼스 또는 입력 컨텍스트와 일치하지 않는 것으로 밝혀진 모델 동작으로 정의됩니다. 사실성에 대한 오라클은 정의하기 어렵고 때로는 논란의 여지가 있을 수 있지만, 환각에 대한 오라클은 모델과 관련하여 내부적으로 정의될 수 있습니다. 우리의 첫 번째 목표는 "환각"을 "사실성"과 분리하여 다양한 유형의 환각을 설명하고 명확히 하며, 일관성을 촉진하고 추가 연구를 용이하게 하는 분류 체계를 제공하는 것입니다.

<figure>
<img src="assets/Figure_1.png" alt="Figure 1">
<figcaption>Figure 1 HalluLens: LLM Hallucination Benchmark. It consists of newly introduced extrinsic hallucination tasks and existing intrinsic hallucination tasks. Extrinsic hallucination test sets are dynamically generated.</figcaption>
</figure>

우리는 텍스트 환각의 두 가지 주요 유형, 즉 "내재적(intrinsic)" 및 "외인성(extrinsic)" 환각이 있다고 생각합니다(Ji et al., 2023). 내재적 환각은 소스 쿼리와 모순되는 생성된 텍스트입니다. 이는 기계 번역이나 텍스트 요약 중에 발생할 수 있으며, 예를 들어 생성된 텍스트에 소스 쿼리와 모순되거나 존재하지 않는 진술이 포함된 경우입니다. 이러한 환각은 일반적으로 소스 쿼리와 관련하여 쉽게 확인할 수 있습니다. 또한 LLM은 직접적인 입력 컨텍스트 없이 콘텐츠를 생성할 수 있으며(Bang et al., 2023; Huang et al., 2023; Zhang et al., 2023; Wang et al., 2023, 2024), 대신 내부 지식에 의존합니다. 예를 들어, LLM은 반드시 컨텍스트 입력을 포함하지 않는 사용자 작업 지침에 따라 자유 형식 텍스트를 생성할 수 있습니다. 오늘날 대부분의 생성 작업은 작업 지침에만 기반합니다. 이러한 경우, 환각된 콘텐츠는 오라클 "진실"이 훈련 데이터 어디에나 있을 수 있으므로 쉽게 확인할 수 없습니다. 이를 "외인성 환각"이라고 하며, 기존 벤치마크로는 적절하게 측정되지 않습니다. 이 연구에서는 외인성 환각을 위해 특별히 설계된 새로운 평가 작업을 소개합니다.

또한, 데이터 유출은 효과적인 벤치마크를 설계하는 데 있어 일반적인 과제입니다(Deng et al., 2024). 이 문제는 LLM 개발의 빠른 발전과 그에 따른 집약적인 주석 노력으로 인해 환각 벤치마크에 특히 심각합니다. 정적 테스트 세트는 새로운 훈련 데이터 세트가 지속적으로 업데이트되고 결과적으로 이러한 테스트 세트를 통합하여 확장됨에 따라 노후화에 특히 취약합니다. 이를 해결하기 위해 우리 벤치마크는 테스트 세트 생성에 동적 접근 방식을 채택하여 유출 위험을 줄이고 시간이 지남에 따라 견고성을 보장하며 신뢰할 수 있는 환각 평가를 보장합니다.

추가적으로, 기존 벤치마크의 통찰력 격차를 해소하기 위해 TruthfulQA(Lin et al., 2022), SimpleQA(Wang et al., 2024), HaluEval2.0(Li et al., 2024)을 포함한 환각 및 사실성에 대한 주요 벤치마크를 분석합니다. 우리는 이러한 벤치마크가 평가하는 특정 과제를 식별하여 그 통찰력이 LLM 개발에 적절하게 적용되도록 합니다. 특히, TruthfulQA에 대한 우리의 분석은 몇 가지 문제를 드러냅니다: 이제 훈련 데이터에 포함되어 포화 상태이며, 잘못된 정답을 포함하고, 그 메트릭은 모델을 과도하게 불이익을 줍니다. 이러한 발견은 기존 벤치마크를 재검토할 필요성을 강조합니다.

따라서 이 연구의 목표는 세 가지입니다: (1) LLM의 환각에 대한 명확한 분류 체계를 수립합니다(§2); (2) 유출로 인한 포화를 방지하기 위해 동적으로 재생성할 수 있는 데이터로 새로운 외인성 환각 평가 작업을 도입합니다(§3); (3) 환각과 사실성 평가를 구별하여 기존 벤치마크에 대한 포괄적인 분석을 제공합니다(§4-5).

## 2 Overview of LLM Hallucination

LLM의 환각은 모델의 성능, 신뢰성 및 신뢰성에 중대한 영향을 미칩니다. 우리는 먼저 기존 LLM 환각 조사가 제안한 분류와 비교하고 낮은 LLM 사실성 문제와 환각을 분리하여 환각 유형을 설명함으로써 명확한 환각 분류 체계를 제공합니다. 그런 다음, 환각의 잠재적 원인도 설명합니다. 마지막으로, 환각 평가 벤치마크 설계 기준을 소개합니다.

<figure>
<img src="assets/Figure_2.png" alt="Figure 2">
<figcaption>Figure 2 Hallucination categories and factuality in LLMs: This diagram shows hallucinations in the two, extrinsic and intrinsic, categories in the blue circles, excluding "factuality" benchmarks. Existing categorizations by Zhang et al. (2023) and Huang et al. (2023) conflate hallucination with factuality and overlook extrinsic hallucination. Tasks in blue are new benchmarks in HalluLens, while the red ones conflate extrinsic hallucination with factuality. The red tasks can be adapted to extrinsic hallucination evaluation with metric modifications. The black benchmarks are suitable for intrinsic hallucinations.</figcaption>
</figure>

### 2.1 Distinction between LLM Hallucination and Factuality

LLM 환각과 사실성의 개념은 생성된 콘텐츠의 신뢰성과 관련이 있지만, 모델 성능의 다른 측면을 다루고 다른 출처를 참조합니다. 이러한 차이점을 이해하는 것은 각각에 대한 효과적인 해결책을 개발하는 데 중요합니다. LLM 사실성 과제는 확립된 검증 출처에 대한 생성된 콘텐츠의 절대적인 정확성을 의미하며(Wang et al., 2024), 사실적 지식을 사용하는 모델의 능력을 강조합니다(Wang et al., 2023). 반면, 환각은 훈련 데이터나 추론 시 입력으로 모델이 접근했던 지식에 대한 모델 출력의 일관성과 관련하여 정의됩니다(Ji et al., 2023). 따라서 주요 구별은 모델의 생성이 평가되는 참조 소스에 있습니다.

환각과 사실성 사이의 얽힘은 자연어 생성의 환각에 대한 초기 연구부터 존재해 왔으며, 이는 주로 불분명한 참조 오라클 때문입니다. LLM이 발전함에 따라, 특히 모델이 특정 입력 소스나 컨텍스트 없이 내부 지식을 기반으로 콘텐츠를 생성할 때 이러한 얽힘은 더욱 복잡해졌습니다. "비상식적이거나 제공된 소스 콘텐츠에 충실하지 않은 생성된 콘텐츠"라는 원래 정의에서 "소스"를 혼동하는 이러한 모호함은(Ji et al., 2023) 최근 일부 연구에서 "검증 가능한 실제 사실"(Huang et al., 2023) 또는 "확립된 세계 지식"(Zhang et al., 2023)을 참조하여 환각의 정의를 사실적 오류를 포함하도록 확장하도록 제안하게 했습니다. 우리의 관점에서, 이러한 확장은 모델 개발 및 환각 완화에 있어 추가적인 복잡성과 어려움을 초래합니다. 우리는 오라클 사실적 지식에 기반한 "사실성"과 사전 훈련 데이터 및 입력 컨텍스트의 오라클에 기반한 "환각"을 구별할 것을 강력히 주장합니다. 이 논문에서는 후자, 즉 환각 벤치마킹에 중점을 둡니다.

LLM의 환각은 사실적으로 잘못된 정보를 초래할 수 있지만 항상 그런 것은 아닙니다. 사실성은 확립된 세계 지식을 기반으로 콘텐츠를 생성하는 것을 의미하지만, 우리는 환각이 사용자 입력 및 훈련 데이터로 제한된 소스와의 일관성에 중점을 둔다고 주장합니다. 환각이 아닌 텍스트도 사실성을 위반할 수 있습니다. 예를 들어, 모델이 시간에 민감한 지식을 포함하는 콘텐츠를 생성할 때입니다. 그림 3은 "최근 하계 올림픽"에 대한 질문을 예로 들어 이 점을 명확히 하는 데 도움이 됩니다. 어떤 경우에는 출력이 사실적으로는 부정확하지만 훈련 데이터와 일치하면 환각이 아닐 수 있습니다. 반대로, 환각된 콘텐츠는 사용자 입력에서 벗어나더라도 외부 참조 지식 소스와 일치하는 한 사실일 수 있습니다. 더욱이, 우리는 논란의 여지가 있는 진술은 훈련 데이터에 뒷받침하는 증거가 있는 한 환각으로 간주하지 않습니다.

환각과 LLM 사실성에는 서로 다른 완화 전략이 필요하며, 진행 상황은 전용 벤치마크를 통해 추적되어야 합니다. 그러나 이러한 과제는 종종 얽혀 있어 명확한 구별 없이 벤치마크를 상호 교환적으로 사용하게 됩니다. 예를 들어, HaluEval(Li et al., 2023b, 2024)은 사실성 및 환각 조사 모두에서 참조됩니다. TruthfulQA(Lin et al., 2022)는 종종 사실성을 측정할 때 환각 벤치마크로 오해됩니다. 미묘한 이해는 전용 평가 작업을 통해 해당 분야를 발전시키는 데 중요합니다. 완화 전략은 다릅니다. 환각 감소 방법 중 하나는 불확실할 때 기권하거나 거부하는 것으로, 이는 환각된 콘텐츠를 방지하지만 사실적 지식을 향상시키지는 않습니다. 사실성은 검색 증강 생성(RAG)과 같은 추가 지식을 제공함으로써 향상될 수 있지만 수동 검사가 여전히 필요할 수 있습니다. 당연히 "환각"을 완화하는 것은 사실성 측면에서 전반적인 모델 개선에 기여할 것입니다.

<figure>
<img src="assets/Figure_3.png" alt="Figure 3">
<figcaption>Figure 3 Examples for each challenge, including extrinsic hallucination, intrinsic hallucination and factuality issues. Note that LLM factuality is not a type of hallucination, yet it is closely tied with hallucination problem in LLM. *As of December 2024.</figcaption>
</figure>

### 2.2 Categories of LLM Hallucination

우리는 Ji et al. (2023)의 원래 분류, 즉 (1) 외인성 환각과 (2) 내인성 환각에 맞춰 LLM의 맥락에서 이를 재정의하고 각 환각 유형에 대한 "주어진 출처"를 명확히 할 것을 제안합니다. 우리는 다음과 같은 유형의 환각을 정의합니다:

*   **외인성 환각:** 훈련 데이터와 일치하지 않는 생성. 입력 컨텍스트에 의해 지원되거나 반박될 수 없습니다. 이러한 환각은 모델이 새로운 콘텐츠(즉, 작업 지침에 기반한 자유 형식 텍스트)를 생성하거나 지식 격차를 메우려고 할 때 종종 발생합니다. 이는 훈련 데이터에서 지식을 흡수하는 모델의 한계와 지식의 경계를 인식하지 못하는 무능력을 반영합니다.
*   **내인성 환각:** 입력 컨텍스트와 일치하지 않는 생성. 모델이 입력 컨텍스트를 올바르게 이해하지 못하면 입력 쿼리와 모순되거나 원래 입력 쿼리에서 지원되지 않는 콘텐츠를 생성합니다. 이는 추론 시 일관성을 유지하지 못하는 모델의 무능력을 반영합니다.

LLM 환각에 대한 두 개의 자주 인용되는 설문 조사(Huang et al., 2023; Zhang et al., 2023)는 LLM의 다재다능함을 설명하고 새로운 분류를 제안하기 위해 Ji et al. (2023)의 환각 정의를 확장했습니다. 그러나 둘 다 LLM의 환각과 사실성을 혼동합니다. 그림 2에서 볼 수 있듯이 Huang et al. (2023)은 환각을 두 가지 유형으로 분류합니다: (i) 사실성 환각(사실적 모순 및 사실적 조작) 및 (ii) 충실도 환각(지시-, 컨텍스트- 및 논리적 불일치). 대조적으로 Zhang et al. (2023)은 세 가지 범주를 제안합니다: (i) 입력-충돌, (ii) 컨텍스트-충돌, (iii) 사실-충돌. 이러한 분류는 모델의 훈련 데이터와의 (불)일치라는 중요한 개념을 포착하지 못합니다. 우리는 모델의 훈련 데이터와 일치하지만 예를 들어 세상이 그 사이에 변했기 때문에 사실적으로 잘못된 답변은 환각으로 간주되어서는 안 된다고 주장합니다.

### 2.3 Potential Sources of Hallucination

환각을 추가로 완화하기 위해 잠재적인 원인을 명시하는 것이 중요합니다. 문헌(Ji et al., 2023; Huang et al., 2023; Zhang et al., 2023)에 따라 환각의 원인을 다음과 같이 나열합니다: (1) 보이지 않거나 제한된 지식; (2) 모순되거나 잡음이 많은 훈련 데이터 및 입력 소스; (3) 모델링 오류.

**Data-Related: Unseen or Limited Knowledge** 훈련 데이터에 관련 정보가 부족하면 모델이 쿼리에 대한 응답을 조작하여 잠재적인 외인성 환각으로 이어질 수 있습니다. 이 문제는 최신 지식이 필요한 쿼리(Kasai et al., 2023; Li et al., 2023a; Onoe et al., 2022), 답할 수 없는 문제(예: 해결되지 않은 과학적 문제)(Yin et al., 2023; Amayuelas et al., 2023) 및 롱테일 지식(Mallen et al., 2023a; Kandpal et al., 2023)과 관련된 쿼리에서 발생합니다. 이러한 경우 LLM은 훈련 데이터에서 지원되지 않는 콘텐츠를 생성할 수 있습니다. 이상적으로 LLM은 지식 경계, 즉 "자신이 모르는 것"을 인식하고 이러한 지식이 필요한 쿼리에 직면했을 때 조작된 콘텐츠를 제공하는 것을 삼가야 합니다(Cheng et al., 2024; Feng et al., 2024).

**Data-Related: Contradictory or Noisy Training Data and Input Source** 훈련 데이터에 상충되거나 잡음이 많은 정보가 포함되어 있으면 모델이 혼란스러워지거나 오도될 수 있습니다(Carlini et al., 2021). 이는 의미론적 이해와 파라메트릭 지식 학습에 도전하여 외인성 및 내인성 환각을 모두 유발할 수 있습니다. 생성된 콘텐츠가 훈련 데이터의 일부에 의해 지원되는 경우, 훈련 데이터와 일치하므로 환각으로 간주되지 않습니다. 그러나 모순된 데이터는 특정 부분과 일치하지 않는 생성을 초래할 수 있습니다. 한편, 자체적으로 일관성이 없거나 훈련 데이터와 모순되는 입력 소스(Ming et al., 2024; Filippova, 2020)는 내인성 환각을 초래할 수 있습니다. 이러한 경우, 실제 응용 프로그램에 대해 지침 준수 또는 사실성이 더 중요한지 결정하는 것이 중요합니다. 입력 소스가 "잘 알려진 사실"과 모순되는 경우, 모델은 지침을 무시하면서 사실성에만 집중하면 환각을 일으킬 수 있습니다.

**Model-Related:** 모델의 트랜스포머 기반 아키텍처 및 어텐션 메커니즘(Hahn, 2020; Chiang and Cholak, 2022), 사전 훈련의 훈련 전략(Tirumala et al., 2023), 미세 조정(Gekhman et al., 2024) RLHF 단계(Lin et al., 2024) 및 디코딩 알고리즘(Li et al., 2024)은 노출 편향이나 환각으로 나타나는 모델링 오류를 도입할 수 있습니다. 예를 들어, (Gekhman et al., 2024)는 미세 조정을 통해 새로운 사실적 지식을 도입하면 LLM이 환각을 일으키도록 장려할 수 있음을 발견했습니다. 환각은 모델이 어려운 지침을 처리할 수 없을 때도 발생합니다(Li et al., 2024). LLM의 독특한 측면은 RLHF가 정렬세를 부과하여 모델이 정렬 후 이전에 습득한 다양한 능력을 잃게 되는 것입니다(Lin et al., 2024). 모델링 관련 소스는 내인성 및 외인성 환각을 모두 유발할 수 있습니다.

### 2.4 Criteria for Hallucination Benchmark

**Robustness against unintentional data leakage:** LLM 훈련 데이터의 대부분이 공개 웹 크롤링 텍스트를 포함하므로, 온라인에서 사용 가능한 많은 벤치마크는 LLM 훈련 과정에서 데이터 오염을 최소화하려는 노력에도 불구하고 훈련 데이터의 일부로 포함되기 쉽습니다. 따라서 기존 벤치마크는 빠르게 쓸모없게 될 수 있으며, 이로 인해 벤치마크 결과가 LLM의 실제 성능과 차이가 날 수 있습니다.¹

**Real-World Applicability:** 좋은 벤치마크는 실제 응용 프로그램 및 사용 사례를 대표해야 하며, 도메인, 작업 및 시나리오 전반에 걸쳐 높은 일반성을 가져야 합니다. 모델 성능의 포괄적이고 현실적인 평가를 보장하기 위해 다양한 주제, 프롬프트 스타일 및 응답 형식(예: 단답형, 장문형 응답)을 다루어야 하며, 벤치마크 자체에 대한 좁은 최적화(Goodhart's law로 알려진 함정)를 장려해서는 안 됩니다. 실제 관련성 및 다양성에 초점을 맞춤으로써 벤치마크는 모델의 기본 능력을 효과적으로 측정할 수 있으며, 단순히 평가 메트릭을 조작하는 능력이 아닙니다.

**Strong stability and high sensitivity:** 벤치마크는 동일한 모델로 측정을 반복할 때 안정적인 결과를 산출해야 하며, 이는 낮은 모델 내 분산으로 나타나고, 높은 민감도를 유지해야 합니다. 즉, 모델 간 분산이 모델 내 분산을 초과해야 합니다. LLM 개발을 지원하기 위해 벤치마크는 프론티어 모델을 포함한 광범위한 모델을 포괄하고 성능 수준을 효과적으로 구별해야 합니다. 이 접근 방식은 모델 개선의 여지를 허용하고 벤치마크가 빠르게 쓸모없게 되는 것을 방지합니다.

**Reproducibility:** LLM 개발에서 합의와 투명성을 조성하기 위해 벤치마크는 재현 가능한 오픈 소스 리소스를 사용하여 설계되어야 합니다.

¹MMLU, TruthfulQA와 같이 널리 사용되는 많은 벤치마크가 오염되었을 가능성이 보고되었습니다(Deng et al., 2024).

## 3 HalluLens (a): Extrinsic Hallucination Evaluation

우리는 훈련 데이터와의 (불)일관성에 초점을 맞춘 외인성 환각에 대한 작업 모음을 소개합니다. 이 벤치마크는 환각의 뚜렷한 원인에 따라 두 가지 주요 범주로 나뉜 세 가지 작업으로 구성됩니다: (1) 모델링 오류 및 (2) 보이지 않거나 제한된 정보로 인한 지식 격차. 모델링 오류의 경우, 정밀한 단답형 답변(PreciseWikiQA)을 평가하고 상세한 장문형 콘텐츠(LongWiki)의 일관성을 보장하는 두 가지 작업이 있습니다. 우리는 대부분의 고급 LLM의 훈련 데이터에 포함되어 있다고 가정하고 Wikipedia를 사용하여 테스트 세트를 구성합니다. 보이지 않는 데이터로 인한 환각을 해결하기 위해, 훈련 데이터를 넘어서는 답할 수 없는 질문(NonExistentRefusal)에 직면했을 때 모델의 동작을 평가합니다. LLM 훈련 데이터 세트의 가변성을 감안할 때, 우리는 완전히 존재하지 않는 정보를 묻는 질문을 만듭니다. 이상적으로, 모델은 정보 부족을 인식하고 답변을 삼가야 합니다. 외인성 환각 벤치마크의 두 가지 주요 기준은 (1) 지식 범위가 훈련 데이터 내에 있는지, (2) 거부가 메트릭에서 평가되는지 여부입니다.

테스트 세트가 암기되거나 유출될 위험을 줄이기 위해, 우리는 평가 중에 새로운 테스트 질문을 동적으로 생성합니다(즉, 고정된 테스트 세트 없음). 이는 콘텐츠가 예측 불가능하고 기존 데이터 세트에서 직접 접근할 수 없도록 보장합니다. 이는 이 역동성이 재현성과 긴장을 유발하기 때문에 사소한 문제가 아닙니다. 따라서 동적 세트는 테스트 세트의 다른 버전에 대해 낮은 분산을 가져야 합니다. 또한, 우리는 평가 프로세스의 견고성과 일반성을 향상시키기 위해 광범위한 주제를 다루도록 작업을 설계합니다.

새로 도입된 세 가지 작업은 다양한 시나리오에 대한 다양하고 포괄적인 적용 범위를 제공하여 다양한 조건에서 모델의 성능을 철저히 평가할 수 있도록 합니다. 그렇게 함으로써 우리 벤치마크는 외인성 환각 측면에서 LLM의 강점과 약점에 대한 더 완전한 이해를 제공합니다.²

1.  **PreciseWikiQA:** 훈련 데이터의 지식을 기반으로 한 짧고 사실을 찾는 쿼리에 대한 모델의 환각 수준을 평가합니다. 질문은 훈련 데이터에 국한되므로 이상적인 모델은 거부 없이 정확한 답변을 제공할 수 있어야 합니다.
2.  **LongWiki:** 훈련 데이터의 지식을 기반으로 한 장문형 콘텐츠 생성에 대한 모델의 환각 수준을 평가합니다.
3.  **NonExistentRefusal:** 자연스럽게 들리는 존재하지 않는 인스턴스와 같이 훈련 데이터를 넘어서는 지식으로 프롬프트될 때 환각된 정보를 생성할 가능성을 평가합니다. 우리는 동물, 식물, 비즈니스, 브랜드와 같은 다양한 도메인에서 자연스럽게 들리는 존재하지 않는 엔티티 이름을 만듭니다. 여기에는 두 가지 하위 작업이 있습니다: (i) MixedEntities (ii) GeneratedEntities.

| Task Name | Example Prompts |
| :--- | :--- |
| PreciseWikiQA | • 1951년 4월에 더글러스 맥아더 장군을 누가 교체했습니까?<br>• IndieWire가 실시한 전 세계 300명 이상의 비평가를 대상으로 한 설문 조사에서 2019년 최고의 외국 영화로 허니랜드가 어떤 순위를 받았습니까?<br>• "Living in the Material World"에서 플루트를 연주한 사람은 누구입니까? |
| LongWiki | • 시티 누르바야 이야기에서 다툭 메링기의 특징은 무엇입니까?<br>• 사이클론 베지사의 레위니옹 섬에 대한 영향에 대해 설명하십시오.<br>• 미디어의 반응과 다양한 작가 및 예술가들의 의견을 포함하여 작품 코미디언을 둘러싼 반응과 논란에 대해 설명하십시오. |
| NonExistentRefusal | • 동물 Penapis lusitanica에 대해 더 알고 싶습니다.<br>• JetPrintIMIO 브랜드의 프린터에 대해 설명해 주시겠습니까?<br>• 홍콩에 있는 Storyhouse라는 서점에 대한 정보를 찾고 있습니다. |

*Table 1 Example prompts for each task facilitate extrinsic hallucination evaluation. The NonExistentRefusal ask information about non-existent instances, thus, the models are expected to abstain from providing any particular information about the non-existent instance.*

우리는 다양한 크기와 다른 제품군의 13개 지침 조정 LLM을 평가했습니다: 10개의 오픈 소스 LLM,

²참고로, 소설 창작과 같이 모델이 일부 비현실적인 사실을 만들어내는 것이 좋은 특정 맥락이 있을 수 있습니다. 이 연구는 대상 사용 사례에 적절할 때 환각을 더 잘 방지하는 방법을 더 잘 이해하기 위해 모델이 외적으로 얼마나 환각을 일으키는지 이해하는 데 중점을 둡니다.

## 4 HalluLens (b): Intrinsic Hallucination Evaluation

내재적 환각은 언어 모델이 입력 컨텍스트와 일치하지 않는 콘텐츠를 생성할 때 발생합니다. 최신 LLM의 경우, 내재적 환각은 사용자가 제공한 입력 컨텍스트에 대해 평가됩니다. 예를 들어, 텍스트 요약 작업에서 원본 콘텐츠가 참조 소스 역할을 합니다. LLM이 더욱 다재다능하고 에이전트처럼 되면서 사용자의 입력 컨텍스트와 출력을 일치시키는 것이 충실도를 유지하는 데 중요해졌으며, 이것이 내재적 환각이 종종 "충실도 환각"이라고 불리는 이유입니다. RAG와 같이 도메인 특정 데이터를 입력 컨텍스트로 사용할 때, 생성된 콘텐츠는 제공된 컨텍스트와 일치해야 하며, 이는 "입력-충돌 환각"이라는 용어로 이어집니다.

내재적 환각은 두 가지 주요 이유로 외인성 환각에 비해 상대적으로 잘 연구되었습니다: (1) LLM이 발전하기 전에도 언어 모델은 소스 입력이 필요한 NLG 작업에서 유망한 성능을 보였고, (2) 검증 소스가 명확하고 잘 정의되어 있습니다. 그러나 내재적 환각은 여전히 해결해야 할 중요한 과제이며, 특히 LLM 기반 시스템에 대한 사용자의 신뢰와 밀접하게 관련될 가능성이 높습니다. 이 섹션에서는 벤치마크가 포화되지 않고 관련성이 있는 내재적 환각 벤치마크로 연구자들을 안내합니다.

기존 벤치마크 분석에서 우리는 섹션 2.4에 설명된 기준을 적용합니다. 외인성 환각에 대한 동적 테스트 세트를 만들어 의도하지 않은 데이터 유출에 대한 견고성을 보장했지만, 주로 평가 문제로 인해 내인성 환각에 대한 동적 테스트 세트를 만드는 데는 어려움이 있습니다. 외인성 환각은 자동으로 생성된 정답을 갖출 수 있지만, 이 접근 방식은 LLM 자체를 심사위원으로 사용하면 내인성 환각을 유발할 수 있으므로 내인성 환각에는 적합하지 않습니다. 내인성 환각에 대한 동적 테스트 세트를 개발하는 것은 유망한 연구 방향입니다. 그 동안 우리는 이 분야에서 LLM의 성능을 평가하기 위해 내인성 환각을 구체적으로 대상으로 하는 잘 인용된 벤치마크에 의존합니다. 구체적으로, 우리는 세 가지 기존 벤치마크를 포함합니다: (1) Hughes Hallucination Evaluation Model (HHEM) (Vectara, 2024) (2) ANAH 2.0 (Ji et al., 2024) - 참조 설정 포함 (3) FaithEval (Ming et al., 2024).

### 4.1 HHEM leaderboard (Vectara, 2024)

널리 사용되는 응용 프로그램, 요약에서 내재적 환각 평가

### 4.2 ANAH 2.0 (w/ reference) (Gu et al., 2024)

입력 소스가 사실적으로 정확할 때 내재적 환각 평가

### 4.3 FaithEval (Ming et al., 2024)

입력 소스가 잡음이 많거나 세계 지식과 모순될 때 내재적 환각 평가.

## 5 Revisiting Existing Benchmarks

이 섹션에서는 TruthfulQA, SimpleQA 및 HaluEval과 같이 사실성 및 환각에 대해 자주 인용되는 벤치마크를 검토합니다. 이러한 벤치마크는 두 컨텍스트 모두에서 자주 참조됩니다. 우리의 논의는 평가 메트릭이 LLM의 환각 및 사실성에 관해 제공하는 통찰력을 이해하는 데 중점을 둡니다. 또한 외인성 환각 벤치마크로 어떻게 조정될 수 있는지 탐구합니다. 작업, 테스트 세트 및 평가 메트릭에 대한 자세한 설명은 부록 C를 참조하십시오.

### 5.1 Revisiting frequently cited benchmark TruthfulQA (Lin et al., 2022).

TruthfulQA는 언어 모델의 사실성, 환각 및 신뢰성을 평가하는 데 자주 사용되는 벤치마크입니다. 이는 언어 모델이 훈련 데이터에 존재하는 인간의 거짓을 내재화할 수 있다는 통찰력을 제공했습니다. 결과적으로 TruthfulQA는 환각, 특히 "사실성 환각"(Zhang et al., 2023; Huang et al., 2023)을 탐지하는 벤치마크로 설문 조사에 자주 등장하며, 사실성 벤치마크(Wang et al., 2023)로도 사용됩니다. 그러나 우리는 TruthfulQA가 주로 사실성 벤치마크이며 환각 벤치마크로 쉽게 적용할 수 없다고 주장합니다.

### 5.2 When Factuality Benchmarks can/cannot be Hallucination Benchmark?

TruthfulQA와 유사하게, 다른 벤치마크들도 종종 환각과 사실성 벤치마크로 간주됩니다. 일부 기존 사실성 벤치마크는 심지어 우리가 제안한 작업인 PreciseWikiQA와 유사합니다. 여러 사실성 벤치마크(예: SimpleQA, PopQA)는 평가 지표를 재구성하여 외인성 환각 벤치마크로 조정될 수 있습니다. 그러나 일부는 훈련 지식 차단 날짜를 넘어선 최신 지식에 대해 평가하므로 환각 벤치마크로 사용될 수 없습니다.

### 5.3 Discussion on existing "factuality hallucination" benchmarks.

최근 몇 년 동안 많은 LLM 환각 관련 연구는 Wang et al. (2023), Huang et al. (2023)의 분류를 따르며, 대부분 사실성/사실-충돌 환각을 언급하는데, 우리는 이를 환각과 구별하여 LLM 사실성으로 분류합니다. 이로 인해 많은 후속 연구에서 벤치마크, 탐지 및 완화에 대한 작업이 사실성 문제인지 외인성 환각 문제인지 명시하지 않고 이러한 사실성 문제를 환각이라고 언급하게 되었습니다. 이러한 벤치마크는 "환각" 벤치마크라고 불리지만, 주로 LLM의 사실성을 다루며, 이는 훈련 데이터를 고려하지 않고 확립된 지식 출처에 대한 생성된 답변의 정확성에 관한 것입니다. 우리는 이러한 사실성 환각 벤치마크가 거부율 측정이 포함되고 데이터 세트가 훈련 데이터에 국한될 때 외인성 환각으로 사용될 수 있다고 주장합니다.

## 6 Related Work

**Taxonomy** 앞에서 논의했듯이, LLM이 발전함에 따라 환각의 범주에 대한 합의가 이루어지지 않았습니다. 최근 설문 조사(Zhang et al., 2023; Huang et al., 2023)는 LLM 사실성 문제와 혼동되는 사실적 오류를 포함하도록 정의를 확장했습니다. 그러나 그들은 LLM 환각 연구에 대한 귀중한 통찰력을 제공하고 해당 분야의 연구 작업에 대한 포괄적인 설문 조사를 제공합니다. LLM 연구의 기하급수적인 발전으로 인해 변화가 빠르게 일어나 일부 다루어진 연구가 관련이 없게 되거나 분류 체계가 발전하게 됩니다. LLM 사실성에 대한 최근 설문 조사(Wang et al., 2023; Augenstein et al., 2024)는 환각 문제와 구별하는 것의 중요성을 강조합니다. 그들은 사실성을 상식, 세계 지식 및 도메인 사실을 포함하는 사실적 정보를 따르는 콘텐츠를 생성하는 LLM의 능력으로 정의합니다(Wang et al., 2023).

**Extrinsic and Intrinsic hallucination Benchmark/Dataset** Sun et al. (2024), Yin et al. (2023)과 같은 여러 연구는 훈련 데이터에서 지식 경계를 인식하는 모델의 능력에 초점을 맞추고 있으며, 이는 우리의 NonExistentRefusal과 유사합니다. Sun et al. (2024)은 LLM이 임의적이거나 불합리한 답변을 제공하는 환각 경향을 평가하기 위해 답할 수 없는 수학 문제로 구성된 UMWP 데이터 세트를 소개합니다. Yin et al. (2023)은 과학적 합의 부족과 같이 본질적으로 답할 수 없는 질문을 포함하는 SelfAware 데이터 세트를 제시합니다. 우리의 PreciseWikiQA와 유사하게, Oh et al.은 엔티티-관계 모델을 기반으로 기존 관계형 데이터베이스를 벤치마크 구성 접근 방식으로 활용합니다. 내재적 환각을 위해 특별히 설계되지는 않았지만, 여러 연구에서 모델이 입력 컨텍스트(즉, 내재적 환각)에서 어떻게 벗어나는지 탐구합니다. 예를 들어, Xie et al. (2024)는 LLM이 파라메트릭 메모리와 모순되는 외부 증거에 직면했을 때 지식 충돌을 어떻게 처리하는지 연구하기 위해 설계된 conflictQA 데이터 세트를 소개합니다. 최근 Jacovi et al. (2025)는 제공된 장문형 소스 자료로 LLM 생성이 얼마나 근거가 있는지 측정하기 위한 벤치마크를 발표했습니다. 최근 연구는 주로 영어 LLM의 환각에 초점을 맞추고 있지만, 이 연구를 다른 언어로 확장하는 것이 중요합니다. HalluQA(Cheng et al., 2023) 및 ANAH(Ji et al., 2024; Gu et al., 2024)와 같은 일부 연구는 중국어 QA 작업에서 환각에 대한 평가 프레임워크를 제공함으로써 기여했습니다.

**Hallucination and/or Factuality Detection** LLM의 환각/사실성 탐지는 환각 평가와는 다른 작업이지만 중요한 분야입니다. 이 연구 라인(Hu et al., 2024; Ji et al., 2024; Liu et al., 2022; Li et al., 2023b; Sadat et al., 2023)은 환각을 자동으로 탐지하는 프레임워크나 모델을 개발하는 것을 목표로 하며, 이는 벤치마크의 "심사위원" 역할을 하거나 완화의 일부로 사용될 수 있습니다.

## 7 Conclusion

결론적으로, 우리는 LLM의 사실성과 구별하고 외인성 및 내인성 유형으로 분류하여 환각의 분류 체계를 제시합니다. 우리는 세 가지 새로 제안된 외인성 환각 평가 작업과 세 가지 기존 내인성 환각 작업을 포함하는 HalluLens를 소개합니다. 우리가 제안한 작업은 모델의 훈련 데이터를 참조하여 모델 생성을 평가함으로써 외인성 환각을 구체적으로 평가하는 것을 목표로 합니다. 이러한 작업은 다양한 시나리오를 다루며 모델 평가의 안정성을 유지하면서 동적으로 테스트 세트를 생성하여 데이터 유출에 대해 강력합니다. 우리는 이 연구에서 소개된 뚜렷한 외인성 환각 벤치마크의 필요성을 강조하고 기존 벤치마크를 재검토함으로써 논문을 마무리합니다.

## Acknowledgement

LLM 환각 주제에 대한 통찰력 있는 논의를 해주신 Lei Yu와 TruthfulQA 벤치마크의 데이터 주석 및 분석에 도움을 주신 GenAI 콘텐츠 엔지니어링 팀의 Whitney Meers와 Austen Gregerson에게 감사드립니다. 또한 논문에 대한 의견을 주신 Delong Chen에게도 감사드립니다. 논문 검토 과정에서 긴밀한 지원을 해주신 Carolyn Krol에게도 감사드립니다.

## References

*   [1] Josh Achiam, Steven Adler, Sandhini Agarwal, Lama Ahmad, Ilge Akkaya, Florencia Leoni Aleman, Diogo Almeida, Janko Altenschmidt, Sam Altman, Shyamal Anadkat, et al. Gpt-4 technical report. arXiv preprint arXiv:2303.08774, 2023.
*   [2] Alfonso Amayuelas, Kyle Wong, Liangming Pan, Wenhu Chen, and William Wang. Knowledge of knowledge: Exploring known-unknowns uncertainty with large language models. arXiv preprint arXiv:2305.13712, 2023.
*   [3] Isabelle Augenstein, Timothy Baldwin, Meeyoung Cha, Tanmoy Chakraborty, Giovanni Luca Ciampaglia, David Corney, Renee DiResta, Emilio Ferrara, Scott Hale, Alon Halevy, et al. Factuality challenges in the era of large language models and opportunities for fact-checking. Nature Machine Intelligence, 6(8):852-863, 2024.
*   [4] Yejin Bang, Samuel Cahyawijaya, Nayeon Lee, Wenliang Dai, Dan Su, Bryan Wilie, Holy Lovenia, Ziwei Ji, Tiezheng Yu, Willy Chung, Quyet V. Do, Yan Xu, and Pascale Fung. A multitask, multilingual, multimodal evaluation of ChatGPT on reasoning, hallucination, and interactivity. In Jong C. Park, Yuki Arase, Baotian Hu, Wei Lu, Derry Wijaya, Ayu Purwarianti, and Adila Alfa Krisnadhi, editors, Proceedings of the 13th International Joint Conference on Natural Language Processing and the 3rd Conference of the Asia-Pacific Chapter of the Association for Computational Linguistics (Volume 1: Long Papers), pages 675-718, Nusa Dua, Bali, November 2023. Association for Computational Linguistics. doi: 10.18653/v1/2023.ijcnlp-main.45. https://aclanthology.org/2023.ijcnlp-main.45.
*   [5] Forrest Bao, Miaoran Li, Rogger Luo, and Ofer Mendelevitch. HHEM-2.1-Open, 2024. https://huggingface.co/vectara/hallucination_evaluation_model.
*   [6] Vera Boteva, Demian Gholipour, Artem Sokolov, and Stefan Riezler. A full-text learning to rank dataset for medical information retrieval. In Advances in Information Retrieval: 38th European Conference on IR Research, ECIR 2016, Padua, Italy, March 20-23, 2016. Proceedings 38, pages 716-722. Springer, 2016.
*   [7] Nicholas Carlini, Florian Tramer, Eric Wallace, Matthew Jagielski, Ariel Herbert-Voss, Katherine Lee, Adam Roberts, Tom Brown, Dawn Song, Ulfar Erlingsson, et al. Extracting training data from large language models. In 30th USENIX Security Symposium (USENIX Security 21), pages 2633-2650, 2021.
*   [8] Qinyuan Cheng, Tianxiang Sun, Wenwei Zhang, Siyin Wang, Xiangyang Liu, Mozhi Zhang, Junliang He, Mianqiu Huang, Zhangyue Yin, Kai Chen, and Xipeng Qiu. Evaluating hallucinations in chinese large language models. CoRR, abs/2310.03368, 2023. doi: 10.48550/arXiv.2310.03368. https://doi.org/10.48550/arXiv.2310.03368.
*   [9] Qinyuan Cheng, Tianxiang Sun, Xiangyang Liu, Wenwei Zhang, Zhangyue Yin, Shimin Li, Linyang Li, Zhengfu He, Kai Chen, and Xipeng Qiu. Can ai assistants know what they don't know? In Forty-first International Conference on Machine Learning, 2024.
*   [10] I Chern, Steffi Chern, Shiqi Chen, Weizhe Yuan, Kehua Feng, Chunting Zhou, Junxian He, Graham Neubig, Pengfei Liu, et al. Factool: Factuality detection in generative ai-a tool augmented framework for multi-task and multi-domain scenarios. arXiv preprint arXiv:2307.13528, 2023.
*   [11] David Chiang and Peter Cholak. Overcoming a theoretical limitation of self-attention. In Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages 7654-7664, 2022.
*   [12] Euirim Choi. Goodwiki dataset. https://www.github.com/euirim/goodwiki, September 2023.
*   [13] Peter Clark, Isaac Cowhey, Oren Etzioni, Tushar Khot, Ashish Sabharwal, Carissa Schoenick, and Oyvind Tafjord. Think you have solved question answering? try arc, the ai2 reasoning challenge. arXiv preprint arXiv:1803.05457, 2018.
*   [14] Bryony Davies. Freud and his cigars, 2020. https://www.freud.org.uk/2020/04/22/freud-and-his-cigars/.
*   [15] Chunyuan Deng, Yilun Zhao, Xiangru Tang, Mark Gerstein, and Arman Cohan. Investigating data contamination in modern benchmarks for large language models. In Kevin Duh, Helena Gomez, and Steven Bethard, editors, Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers), pages 8706-8719, Mexico City, Mexico, June 2024. Association for Computational Linguistics. doi: 10.18653/v1/2024.naacl-long.482. https://aclanthology.org/2024.naacl-long.482.
*   [16] Dheeru Dua, Yizhong Wang, Pradeep Dasigi, Gabriel Stanovsky, Sameer Singh, and Matt Gardner. DROP: A reading comprehension benchmark requiring discrete reasoning over paragraphs. In Jill Burstein, Christy Doran, and Thamar Solorio, editors, Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers), pages 2368-2378, Minneapolis, Minnesota, June 2019. Association for Computational Linguistics. doi: 10.18653/v1/N19-1246. https://aclanthology.org/N19-1246.
*   [17] Matthew Dunn, Levent Sagun, Mike Higgins, V Ugur Guney, Volkan Cirik, and Kyunghyun Cho. Searchqa: A new q&a dataset augmented with context from a search engine. arXiv preprint arXiv:1704.05179, 2017.
*   [18] Shangbin Feng, Weijia Shi, Yike Wang, Wenxuan Ding, Vidhisha Balachandran, and Yulia Tsvetkov. Don't hallucinate, abstain: Identifying llm knowledge gaps via multi-llm collaboration. ACL, 2024.
*   [19] Katja Filippova. Controlled hallucinations: Learning to generate faithfully from noisy data. In Findings of the Association for Computational Linguistics: EMNLP 2020, pages 864-870, 2020.
*   [20] Zorik Gekhman, Gal Yona, Roee Aharoni, Matan Eyal, Amir Feder, Roi Reichart, and Jonathan Herzig. Does fine-tuning LLMs on new knowledge encourage hallucinations? In Yaser Al-Onaizan, Mohit Bansal, and Yun-Nung Chen, editors, Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing, pages 7765-7784, Miami, Florida, USA, November 2024. Association for Computational Linguistics. doi: 10.18653/v1/2024.emnlp-main.444. https://aclanthology.org/2024.emnlp-main.444.
*   [21] Yuzhe Gu, Ziwei Ji, Wenwei Zhang, Chengqi Lyu, Dahua Lin, and Kai Chen. ANAH-v2: Scaling analytical hallucination annotation of large language models. In The Thirty-eighth Annual Conference on Neural Information Processing Systems, 2024. https://openreview.net/forum?id=NrwASKGm7A.
*   [22] Michael Hahn. Theoretical limitations of self-attention in neural sequence models. Transactions of the Association for Computational Linguistics, 8:156-171, 2020.
*   [23] Karl Moritz Hermann, Tomas Kocisky, Edward Grefenstette, Lasse Espeholt, Will Kay, Mustafa Suleyman, and Phil Blunsom. Teaching machines to read and comprehend. Advances in neural information processing systems, 28, 2015.
*   [24] Xiangkun Hu, Dongyu Ru, Lin Qiu, Qipeng Guo, Tianhang Zhang, Yang Xu, Yun Luo, Pengfei Liu, Yue Zhang, and Zheng Zhang. Refchecker: Reference-based fine-grained hallucination checker and benchmark for large language models. arXiv preprint arXiv:2405.14486, 2024.
*   [25] Lei Huang, Weijiang Yu, Weitao Ma, Weihong Zhong, Zhangyin Feng, Haotian Wang, Qianglong Chen, Weihua Peng, Xiaocheng Feng, Bing Qin, et al. A survey on hallucination in large language models: Principles, taxonomy, challenges, and open questions. arXiv preprint arXiv:2311.05232, 2023.
*   [26] Integrated Taxonomic Information System ITIS, 2024. Retrieved [month, day, year], from the Integrated Taxonomic Information System (ITIS) on-line database, www.itis.gov, CCO, https://doi.org/10.5066/F7KH0KBK.
*   [27] Alon Jacovi, Andrew Wang, Chris Alberti, Connie Tao, Jon Lipovetz, Kate Olszewska, Lukas Haas, Michelle Liu, Nate Keating, Adam Bloniarz, et al. The facts grounding leaderboard: Benchmarking llms' ability to ground responses to long-form input. arXiv preprint arXiv:2501.03200, 2025.
*   [28] Ziwei Ji, Nayeon Lee, Rita Frieske, Tiezheng Yu, Dan Su, Yan Xu, Etsuko Ishii, Ye Jin Bang, Andrea Madotto, and Pascale Fung. Survey of hallucination in natural language generation. ACM Computing Surveys, 55(12):1-38, March 2023. ISSN 1557-7341. doi: 10.1145/3571730. http://dx.doi.org/10.1145/3571730.
*   [29] Ziwei Ji, Yuzhe Gu, Wenwei Zhang, Chengqi Lyu, Dahua Lin, and Kai Chen. ANAH: Analytical annotation of hallucinations in large language models. In Lun-Wei Ku, Andre Martins, and Vivek Srikumar, editors, Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages 8135-8158, Bangkok, Thailand, August 2024. Association for Computational Linguistics. doi: 10.18653/v1/2024.acl-long.442. https://aclanthology.org/2024.acl-long.442.
*   [30] Mandar Joshi, Eunsol Choi, Daniel Weld, and Luke Zettlemoyer. TriviaQA: A large scale distantly supervised challenge dataset for reading comprehension. In Regina Barzilay and Min-Yen Kan, editors, Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages 1601-1611, Vancouver, Canada, July 2017. Association for Computational Linguistics. doi: 10.18653/v1/P17-1147. https://aclanthology.org/P17-1147.
*   [31] Nikhil Kandpal, Haikang Deng, Adam Roberts, Eric Wallace, and Colin Raffel. Large language models struggle to learn long-tail knowledge. In International Conference on Machine Learning, pages 15696-15707. PMLR, 2023.
*   [32] Jungo Kasai, Keisuke Sakaguchi, yoichi takahashi, Ronan Le Bras, Akari Asai, Xinyan Velocity Yu, Dragomir Radev, Noah A. Smith, Yejin Choi, and Kentaro Inui. Realtime QA: What's the answer right now? In Thirty-seventh Conference on Neural Information Processing Systems Datasets and Benchmarks Track, 2023. https://openreview.net/forum?id=HfKOIPCvsv.
*   [33] Matthew H Kim, Sammy F Ahmed, and Frederick J Morrison. The effects of kindergarten and first grade schooling on executive function and academic skill development: Evidence from a school cutoff design. Frontiers in Psychology, 11:607973, 2021.
*   [34] Tom Kwiatkowski, Jennimaria Palomaki, Olivia Redfield, Michael Collins, Ankur Parikh, Chris Alberti, Danielle Epstein, Illia Polosukhin, Jacob Devlin, Kenton Lee, Kristina Toutanova, Llion Jones, Matthew Kelcey, Ming-Wei Chang, Andrew M. Dai, Jakob Uszkoreit, Quoc Le, and Slav Petrov. Natural questions: A benchmark for question answering research. Transactions of the Association for Computational Linguistics, 7:452-466, 2019. doi: 10.1162/tacl_a_00276. https://aclanthology.org/Q19-1026.
*   [35] Guokun Lai, Qizhe Xie, Hanxiao Liu, Yiming Yang, and Eduard Hovy. RACE: Large-scale ReAding comprehension dataset from examinations. In Martha Palmer, Rebecca Hwa, and Sebastian Riedel, editors, Proceedings of the 2017 Conference on Empirical Methods in Natural Language Processing, pages 785-794, Copenhagen, Denmark, September 2017. Association for Computational Linguistics. doi: 10.18653/v1/D17-1082. https://aclanthology.org/D17-1082.
*   [36] Laboratory for Web Algorithmics Università degli Studi di Milano LAW. The open wikipedia ranking 2024, 2024. https://wikirank-2024.di.unimi.it/.
*   [37] Daliang Li, Ankit Singh Rawat, Manzil Zaheer, Xin Wang, Michal Lukasik, Andreas Veit, Felix Yu, and Sanjiv Kumar. Large language models with controllable working memory. In Findings of the Association for Computational Linguistics: ACL 2023, pages 1774-1793, 2023a.
*   [38] Junyi Li, Xiaoxue Cheng, Wayne Xin Zhao, Jian-Yun Nie, and Ji-Rong Wen. Halueval: A large-scale hallucination evaluation benchmark for large language models. In Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing, pages 6449-6464, 2023b.
