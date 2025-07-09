# Attention Is All You Need

Ashish Vaswani*
Google Brain
avaswani@google.com

Noam Shazeer*
Google Brain
noam@google.com

Niki Parmar*
Google Research
nikip@google.com

Jakob Uszkoreit*
Google Research
usz@google.com

Llion Jones*
Google Research
llion@google.com

Aidan N. Gomez*†
University of Toronto
aidan@cs.toronto.edu

Łukasz Kaiser*
Google Brain
lukaszkaiser@google.com

Illia Polosukhin*‡
illia.polosukhin@gmail.com

> *동일 기여. 저자 순서는 무작위입니다. Jakob은 RNN을 self-attention으로 대체할 것을 제안하고 이 아이디어를 평가하는 노력을 시작했습니다. Ashish는 Illia와 함께 첫 Transformer model을 설계하고 구현했으며, 이 작업의 모든 측면에 결정적으로 참여했습니다. Noam은 scaled dot-product attention, multi-head attention, 그리고 파라미터 없는 position representation을 제안했으며, 거의 모든 세부 사항에 참여한 또 다른 한 명이 되었습니다. Niki는 우리의 원래 코드베이스와 tensor2tensor에서 수많은 model 변형을 설계, 구현, 튜닝 및 평가했습니다. Llion 또한 새로운 model 변형을 실험했으며, 우리의 초기 코드베이스와 효율적인 추론 및 시각화를 담당했습니다. Lukasz와 Aidan은 수많은 긴 날들을 다양한 부분을 설계하고 tensor2tensor를 구현하며 보냈고, 우리의 이전 코드베이스를 대체하여 결과를 크게 개선하고 연구를 대규모로 가속화했습니다.
>
> †Google Brain에서 작업 수행.
> 
> ‡Google Research에서 작업 수행.

## Abstract

지배적인 sequence transduction model은 encoder와 decoder를 포함하는 복잡한 recurrent 또는 convolutional neural network에 기반합니다. 가장 성능이 좋은 model들은 또한 attention 메커니즘을 통해 encoder와 decoder를 연결합니다. 우리는 recurrence와 convolution을 완전히 배제하고 오직 attention 메커니즘에만 기반한 새로운 간단한 네트워크 아키텍처인 **Transformer**를 제안합니다. 두 가지 기계 번역 과제에 대한 실험 결과, 이 model들은 품질 면에서 우수하면서도 병렬화가 더 용이하고 훈련 시간이 훨씬 적게 소요됨을 보여줍니다. 우리 model은 WMT 2014 영어-독일어 번역 과제에서 28.4 BLEU를 달성하여, 기존 최고 결과(앙상블 포함)를 2 BLEU 이상 개선했습니다. WMT 2014 영어-프랑스어 번역 과제에서는 8개의 GPU로 3.5일 동안 훈련한 후 41.8이라는 새로운 단일 model 최고 BLEU 점수를 기록했으며, 이는 기존 최고 model들의 훈련 비용의 일부에 불과합니다. 우리는 Transformer가 대규모 및 제한된 훈련 데이터 모두를 사용하여 영어 구문 분석(English constituency parsing)에 성공적으로 적용됨으로써 다른 과제에도 잘 일반화됨을 보여줍니다.

## 1. 소개

recurrent neural network, 특히 long short-term memory(LSTM) [13](#ref13) 및 gated recurrent [7](#ref7) neural network는 언어 모델링 및 기계 번역과 같은 sequence modeling 및 transduction 문제에서 최고 수준의 접근 방식으로 확고히 자리 잡았습니다 [35](#ref35), [2](#ref2), [5](#ref5). 이후 수많은 노력이 recurrent language model과 encoder-decoder 아키텍처의 한계를 계속해서 넓혀왔습니다 [38](#ref38), [24](#ref24), [15](#ref15).

Recurrent model은 일반적으로 입력 및 출력 sequence의 심볼 위치를 따라 계산을 분해합니다. 위치를 계산 시간 단계에 맞춰, 이전 hidden state $h_{t-1}$과 위치 $t$의 입력에 대한 함수로 hidden state $h_t$의 sequence를 생성합니다. 이러한 본질적인 순차적 특성은 훈련 예제 내에서의 병렬화를 배제하며, 이는 메모리 제약으로 인해 예제 간의 배치가 제한되는 더 긴 sequence 길이에서 치명적이 됩니다. 최근 연구들은 인수분해 트릭 [21](#ref21)과 조건부 계산 [32](#ref32)을 통해 계산 효율성에서 상당한 개선을 이루었으며, 후자의 경우 model 성능도 향상시켰습니다. 그러나 순차적 계산의 근본적인 제약은 여전히 남아있습니다.

Attention 메커니즘은 다양한 과제에서 설득력 있는 sequence modeling 및 transduction model의 필수적인 부분이 되어, 입력 또는 출력 sequence에서의 거리에 관계없이 의존성을 모델링할 수 있게 해줍니다 [2](#ref2), [19](#ref19). 그러나 몇 가지 경우를 제외하고 [27](#ref27), 이러한 attention 메커니즘은 recurrent network와 함께 사용됩니다.

이 연구에서 우리는 recurrence를 배제하고 대신 전적으로 attention 메커니즘에 의존하여 입력과 출력 간의 전역 의존성을 도출하는 model 아키텍처인 Transformer를 제안합니다. Transformer는 훨씬 더 많은 병렬화를 허용하며 8개의 P100 GPU에서 단 12시간 동안 훈련한 후 번역 품질에서 새로운 최고 수준에 도달할 수 있습니다.

## 2. 배경

순차적 계산을 줄이는 목표는 Extended Neural GPU [16](#ref16), ByteNet [18](#ref18], ConvS2S [9](#ref9)의 기초를 형성하며, 이들 모두는 convolutional neural network를 기본 빌딩 블록으로 사용하여 모든 입력 및 출력 위치에 대한 hidden representation을 병렬로 계산합니다. 이러한 model에서 두 임의의 입력 또는 출력 위치의 신호를 관련시키는 데 필요한 연산 수는 위치 간의 거리에 따라 증가하는데, ConvS2S의 경우 선형적으로, ByteNet의 경우 로그적으로 증가합니다. 이로 인해 먼 위치 간의 의존성을 학습하기가 더 어려워집니다 [12](#ref12). Transformer에서는 이를 상수 시간의 연산으로 줄이지만, 이는 attention-weighted position을 평균화함으로써 효과적인 해상도가 감소하는 비용을 수반합니다. 우리는 섹션 3.2에서 설명하는 Multi-Head Attention으로 이 효과를 상쇄합니다.

Self-attention, 때로는 intra-attention이라고도 불리는 것은 단일 sequence의 다른 위치들을 관련시켜 sequence의 representation을 계산하는 attention 메커니즘입니다. Self-attention은 독해, 추상적 요약, 텍스트 함의, 그리고 과제 독립적인 문장 representation 학습 등 다양한 과제에서 성공적으로 사용되었습니다 [4](#ref4), [27](#ref27), [28](#ref28), [22](#ref22).

End-to-end memory network는 sequence-aligned recurrence 대신 recurrent attention 메커니즘에 기반하며, 간단한 언어 질의응답 및 언어 모델링 과제에서 좋은 성능을 보여주었습니다 [34](#ref34).

그러나 우리가 아는 한, Transformer는 sequence-aligned RNN이나 convolution을 사용하지 않고 입력과 출력의 representation을 계산하기 위해 전적으로 self-attention에 의존하는 최초의 transduction model입니다. 다음 섹션에서는 Transformer를 설명하고, self-attention을 동기 부여하며, [17](#ref17), [18](#ref18), [9](#ref9)와 같은 model에 대한 장점을 논의할 것입니다.

## 3. Model Architecture

대부분의 경쟁력 있는 neural sequence transduction model은 encoder-decoder 구조를 가지고 있습니다 [5](#ref5), [2](#ref2), [35](#ref35). 여기서 encoder는 심볼 representation의 입력 sequence $(x_1, ..., x_n)$을 연속적인 representation의 sequence $\mathbf{z} = (z_1, ..., z_n)$으로 매핑합니다. $\mathbf{z}$가 주어지면, decoder는 한 번에 하나의 요소를 생성하여 심볼의 출력 sequence $(y_1, ..., y_m)$를 생성합니다. 각 단계에서 model은 이전에 생성된 심볼을 다음 심볼을 생성할 때 추가 입력으로 사용하여 auto-regressive합니다 [10](#ref10).

Transformer는 Figure 1의 왼쪽과 오른쪽 절반에 각각 표시된 것처럼, encoder와 decoder 모두에 대해 stacked self-attention과 point-wise, fully connected layer를 사용하는 전체적인 아키텍처를 따릅니다.

<figure>
    <img src="assets/figure_1.png" alt="Figure 1">
    <figcaption><p>Figure 1: The Transformer - model architecture.</p></figcaption>
</figure>

### 3.1 Encoder and Decoder Stacks

**Encoder**: encoder는 $N=6$개의 동일한 layer 스택으로 구성됩니다. 각 layer에는 두 개의 sub-layer가 있습니다. 첫 번째는 multi-head self-attention 메커니즘이고, 두 번째는 간단한, position-wise fully connected feed-forward network입니다. 우리는 두 sub-layer 각각에 residual connection [11](#ref11)을 적용하고, 그 다음에 layer normalization [1](#ref1)을 적용합니다. 즉, 각 sub-layer의 출력은 $\text{LayerNorm}(x + \text{Sublayer}(x))$이며, 여기서 $\text{Sublayer}(x)$는 sub-layer 자체에 의해 구현된 함수입니다. 이러한 residual connection을 용이하게 하기 위해, model의 모든 sub-layer와 embedding layer는 차원 $d_{\text{model}} = 512$의 출력을 생성합니다.

**Decoder**: decoder 또한 $N=6$개의 동일한 layer 스택으로 구성됩니다. 각 encoder layer의 두 sub-layer 외에, decoder는 encoder 스택의 출력에 대해 multi-head attention을 수행하는 세 번째 sub-layer를 삽입합니다. encoder와 유사하게, 우리는 각 sub-layer 주위에 residual connection을 사용하고 그 다음에 layer normalization을 적용합니다. 또한 decoder 스택의 self-attention sub-layer를 수정하여 위치가 후속 위치에 attend하는 것을 방지합니다. 이 마스킹은 출력 embedding이 한 위치만큼 오프셋된다는 사실과 결합하여, 위치 $i$에 대한 예측이 $i$보다 작은 위치의 알려진 출력에만 의존하도록 보장합니다.

### 3.2 Attention

Attention 함수는 query와 key-value 쌍 집합을 출력에 매핑하는 것으로 설명할 수 있으며, 여기서 query, key, value 및 출력은 모두 벡터입니다. 출력은 value의 가중 합으로 계산되며, 각 value에 할당된 가중치는 해당 key와 query의 호환성 함수에 의해 계산됩니다.

<figure>
    <img src="assets/figure_2.png" alt="Figure 2">
    <figcaption><p>Figure 2: (left) Scaled Dot-Product Attention. (right) Multi-Head Attention consists of several attention layers running in parallel.</p></figcaption>
</figure>

#### 3.2.1 Scaled Dot-Product Attention

우리는 우리의 특정 attention을 "Scaled Dot-Product Attention"이라고 부릅니다 (Figure 2). 입력은 차원 $d_k$의 query와 key, 그리고 차원 $d_v$의 value로 구성됩니다. 우리는 query와 모든 key의 dot product를 계산하고, 각각을 $\sqrt{d_k}$로 나눈 다음, value에 대한 가중치를 얻기 위해 softmax 함수를 적용합니다.

실제로, 우리는 attention 함수를 행렬 $Q$로 함께 묶인 query 집합에 대해 동시에 계산합니다. key와 value도 행렬 $K$와 $V$로 함께 묶입니다. 우리는 출력 행렬을 다음과 같이 계산합니다:

$$
\text{Attention}(Q, K, V) = \text{softmax}(\frac{QK^T}{\sqrt{d_k}})V
$$

가장 일반적으로 사용되는 두 가지 attention 함수는 additive attention [2](#ref2)과 dot-product (multiplicative) attention입니다. Dot-product attention은 우리의 알고리즘과 동일하며, 스케일링 팩터 $\frac{1}{\sqrt{d_k}}$만 다릅니다. Additive attention은 단일 hidden layer를 가진 feed-forward network를 사용하여 호환성 함수를 계산합니다. 이 둘은 이론적인 복잡성은 비슷하지만, dot-product attention은 고도로 최적화된 행렬 곱셈 코드를 사용하여 구현할 수 있기 때문에 실제로는 훨씬 빠르고 공간 효율적입니다.

$d_k$의 작은 값에 대해서는 두 메커니즘이 비슷하게 수행되지만, $d_k$의 큰 값에 대해서는 스케일링 없이 dot product attention보다 additive attention이 더 뛰어납니다 [3](#ref3). 우리는 $d_k$의 큰 값에 대해 dot product가 크기가 커져 softmax 함수를 극도로 작은 기울기를 가진 영역으로 밀어 넣는다고 의심합니다. 이를 상쇄하기 위해, 우리는 dot product를 $\frac{1}{\sqrt{d_k}}$로 스케일링합니다.

#### 3.2.2 Multi-Head Attention

$d_{\text{model}}$ 차원의 key, value, query를 사용하여 단일 attention 함수를 수행하는 대신, 우리는 query, key, value를 각각 다른, 학습된 선형 프로젝션을 사용하여 $h$번 $d_k$, $d_k$, $d_v$ 차원으로 선형적으로 투영하는 것이 유익하다는 것을 발견했습니다. 이러한 각 투영된 버전의 query, key, value에 대해 우리는 병렬로 attention 함수를 수행하여 $d_v$ 차원의 출력 값을 생성합니다. 이들은 Figure 2에서 보듯이 연결되고 다시 한 번 투영되어 최종 값을 생성합니다.

Multi-head attention은 model이 다른 위치의 다른 representation 부분 공간에서 온 정보에 공동으로 attend하도록 허용합니다. 단일 attention head에서는 평균화가 이를 억제합니다.

$$
\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, ..., \text{head}_h)W^O \\
\text{where head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)
$$

여기서 프로젝션은 파라미터 행렬 $W_i^Q \in \mathbb{R}^{d_{\text{model}} \times d_k}$, $W_i^K \in \mathbb{R}^{d_{\text{model}} \times d_k}$, $W_i^V \in \mathbb{R}^{d_{\text{model}} \times d_v}$ 및 $W^O \in \mathbb{R}^{hd_v \times d_{\text{model}}}$입니다.

이 연구에서 우리는 $h=8$개의 병렬 attention layer, 즉 head를 사용합니다. 각각에 대해 $d_k = d_v = d_{\text{model}}/h = 64$를 사용합니다. 각 head의 차원 감소로 인해, 총 계산 비용은 전체 차원을 가진 단일 head attention과 유사합니다.

#### 3.2.3 우리 Model에서의 Attention 적용

Transformer는 multi-head attention을 세 가지 다른 방식으로 사용합니다:

*   "encoder-decoder attention" layer에서, query는 이전 decoder layer에서 오고, memory key와 value는 encoder의 출력에서 옵니다. 이를 통해 decoder의 모든 위치가 입력 sequence의 모든 위치에 attend할 수 있습니다. 이는 [38](#ref38), [2](#ref2), [9](#ref9)와 같은 sequence-to-sequence model에서 일반적인 encoder-decoder attention 메커니즘을 모방합니다.
*   encoder는 self-attention layer를 포함합니다. self-attention layer에서 모든 key, value, query는 같은 장소, 이 경우 encoder의 이전 layer의 출력에서 옵니다. encoder의 각 위치는 encoder의 이전 layer의 모든 위치에 attend할 수 있습니다.
*   유사하게, decoder의 self-attention layer는 decoder의 각 위치가 해당 위치까지 포함하여 decoder의 모든 위치에 attend하도록 허용합니다. 우리는 auto-regressive 속성을 보존하기 위해 decoder에서 왼쪽으로의 정보 흐름을 방지해야 합니다. 우리는 scaled dot-product attention 내부에서 softmax의 입력에서 불법적인 연결에 해당하는 모든 값을 마스킹(음의 무한대로 설정)하여 이를 구현합니다. Figure 2를 참조하십시오.

### 3.3 Position-wise Feed-Forward Networks

attention sub-layer 외에도, 우리 encoder와 decoder의 각 layer는 fully connected feed-forward network를 포함하며, 이는 각 위치에 개별적으로 그리고 동일하게 적용됩니다. 이는 두 개의 선형 변환과 그 사이에 ReLU 활성화 함수로 구성됩니다.

$$
\text{FFN}(x) = \max(0, xW_1 + b_1)W_2 + b_2
$$

선형 변환은 다른 위치에 걸쳐 동일하지만, layer마다 다른 파라미터를 사용합니다. 이를 설명하는 또 다른 방법은 커널 크기가 1인 두 개의 convolution으로 볼 수 있습니다. 입력과 출력의 차원은 $d_{\text{model}} = 512$이고, 내부 layer의 차원은 $d_{ff} = 2048$입니다.

### 3.4 Embeddings and Softmax

다른 sequence transduction model과 유사하게, 우리는 학습된 embedding을 사용하여 입력 토큰과 출력 토큰을 차원 $d_{\text{model}}$의 벡터로 변환합니다. 또한 일반적인 학습된 선형 변환과 softmax 함수를 사용하여 decoder 출력을 예측된 다음 토큰 확률로 변환합니다. 우리 model에서는 두 embedding layer와 pre-softmax 선형 변환 간에 동일한 가중치 행렬을 공유합니다 [30](#ref30]. embedding layer에서는 이 가중치에 $\sqrt{d_{\text{model}}}$을 곱합니다.

### 3.5 Positional Encoding

우리 model은 recurrence나 convolution을 포함하지 않으므로, model이 sequence의 순서를 활용하려면 sequence에 있는 토큰의 상대적 또는 절대적 위치에 대한 정보를 주입해야 합니다. 이를 위해, 우리는 encoder와 decoder 스택의 맨 아래에 있는 입력 embedding에 "positional encoding"을 추가합니다. positional encoding은 embedding과 동일한 차원 $d_{\text{model}}$을 가지므로 둘을 합산할 수 있습니다. positional encoding에는 학습된 것과 고정된 것 등 여러 선택지가 있습니다 [9](#ref9).

이 연구에서 우리는 다른 주파수의 사인 및 코사인 함수를 사용합니다:

$$
PE_{(pos, 2i)} = \sin(pos / 10000^{2i/d_{\text{model}}})
$$
$$
PE_{(pos, 2i+1)} = \cos(pos / 10000^{2i/d_{\text{model}}})
$$

여기서 $pos$는 위치이고 $i$는 차원입니다. 즉, positional encoding의 각 차원은 사인파에 해당합니다. 파장은 $2\pi$에서 $10000 \cdot 2\pi$까지 기하급수적으로 증가합니다. 우리는 이 함수를 선택했는데, 고정된 오프셋 $k$에 대해 $PE_{pos+k}$가 $PE_{pos}$의 선형 함수로 표현될 수 있기 때문에 model이 상대적 위치에 의해 쉽게 attend하는 법을 배울 수 있을 것이라고 가정했기 때문입니다.

또한 학습된 positional embedding [9](#ref9)을 사용하는 실험도 진행했으며, 두 버전이 거의 동일한 결과를 생성한다는 것을 발견했습니다(Table 3 행 (E) 참조). 우리는 사인파 버전을 선택했는데, 이는 model이 훈련 중에 마주친 것보다 긴 sequence 길이에 대해 외삽할 수 있기 때문일 수 있습니다.

## 4. 왜 Self-Attention인가

이 섹션에서는 self-attention layer를 가변 길이의 심볼 representation sequence $(x_1, ..., x_n)$을 동일한 길이의 다른 sequence $(z_1, ..., z_n)$(여기서 $x_i, z_i \in \mathbb{R}^d$)로 매핑하는 데 일반적으로 사용되는 recurrent 및 convolutional layer와 비교합니다. 예를 들어, 일반적인 sequence transduction encoder 또는 decoder의 hidden layer가 있습니다. self-attention을 사용하는 동기를 부여하기 위해 우리는 세 가지 바람직한 점을 고려합니다.

하나는 layer당 총 계산 복잡성입니다. 다른 하나는 병렬화할 수 있는 계산의 양으로, 필요한 최소 순차 연산 수로 측정됩니다.

세 번째는 네트워크에서 장거리 의존성 간의 경로 길이입니다. 많은 sequence transduction 과제에서 장거리 의존성을 학습하는 것이 핵심적인 과제입니다. 이러한 의존성을 학습하는 능력에 영향을 미치는 한 가지 핵심 요소는 신호가 네트워크를 통해 순방향 및 역방향으로 이동해야 하는 경로의 길이입니다. 입력과 출력 sequence의 위치 조합 간의 경로가 짧을수록 장거리 의존성을 배우기가 더 쉽습니다 [12](#ref12). 따라서 우리는 다른 layer 유형으로 구성된 네트워크에서 임의의 두 입력 및 출력 위치 간의 최대 경로 길이도 비교합니다.

Table 1에서 언급했듯이, self-attention layer는 모든 위치를 상수 개의 순차적으로 실행되는 연산으로 연결하는 반면, recurrent layer는 $O(n)$ 순차 연산을 필요로 합니다. 계산 복잡성 측면에서, sequence 길이 $n$이 representation 차원 $d$보다 작을 때 self-attention layer는 recurrent layer보다 빠릅니다. 이는 기계 번역에서 state-of-the-art model이 사용하는 문장 representation(예: word-piece [38](#ref38) 및 byte-pair [31](#ref31] representation)에서 가장 흔한 경우입니다. 매우 긴 sequence를 포함하는 과제에 대한 계산 성능을 향상시키기 위해, self-attention은 해당 출력 위치를 중심으로 하는 입력 sequence의 크기 $r$인 이웃만 고려하도록 제한될 수 있습니다. 이는 최대 경로 길이를 $O(n/r)$로 증가시킬 것입니다. 우리는 향후 연구에서 이 접근법을 더 조사할 계획입니다.

커널 너비 $k < n$인 단일 convolutional layer는 모든 입력 및 출력 위치 쌍을 연결하지 않습니다. 이를 위해서는 인접 커널의 경우 $O(n/k)$개의 convolutional layer 스택이 필요하거나, dilated convolution [18](#ref18)의 경우 $O(\log_k(n))$이 필요하여 네트워크에서 임의의 두 위치 간의 가장 긴 경로의 길이를 증가시킵니다. Convolutional layer는 일반적으로 recurrent layer보다 $k$배 더 비쌉니다. 그러나 Separable convolution [6](#ref6]은 복잡성을 $O(k \cdot n \cdot d + n \cdot d^2)$로 상당히 감소시킵니다. 그러나 $k=n$인 경우에도, separable convolution의 복잡성은 self-attention layer와 point-wise feed-forward layer의 조합과 동일하며, 이는 우리 model에서 취하는 접근 방식입니다.

부수적인 이점으로, self-attention은 더 해석 가능한 model을 산출할 수 있습니다. 우리는 우리 model의 attention 분포를 검사하고 부록에서 예제를 제시하고 논의합니다. 개별 attention head는 명확하게 다른 작업을 수행하는 법을 배울 뿐만 아니라, 많은 경우 문장의 구문 및 의미 구조와 관련된 행동을 보입니다.

| Layer Type | Complexity per Layer | Sequential Operations | Maximum Path Length |
| :--- | :--- | :--- | :--- |
| Self-Attention | $O(n^2 \cdot d)$ | $O(1)$ | $O(1)$ |
| Recurrent | $O(n \cdot d^2)$ | $O(n)$ | $O(n)$ |
| Convolutional | $O(k \cdot n \cdot d^2)$ | $O(1)$ | $O(\log_k(n))$ |
| Self-Attention (restricted) | $O(r \cdot n \cdot d)$ | $O(1)$ | $O(n/r)$ |
<p align="center">Table 1: 다른 layer 유형에 대한 최대 경로 길이, layer당 복잡성 및 최소 순차 연산 수. $n$은 sequence 길이, $d$는 representation 차원, $k$는 convolution의 커널 크기, $r$은 제한된 self-attention의 이웃 크기입니다.</p>

## 5. 훈련

이 섹션에서는 우리 model의 훈련 체제를 설명합니다.

### 5.1 훈련 데이터 및 배치

우리는 약 450만 개의 문장 쌍으로 구성된 표준 WMT 2014 영어-독일어 데이터셋에서 훈련했습니다. 문장은 약 37,000개의 토큰으로 구성된 공유 소스-타겟 어휘를 가진 byte-pair encoding [3](#ref3)을 사용하여 인코딩되었습니다. 영어-프랑스어의 경우, 우리는 3,600만 개의 문장으로 구성된 훨씬 더 큰 WMT 2014 영어-프랑스어 데이터셋을 사용하고 토큰을 32,000개의 word-piece 어휘로 분할했습니다 [38](#ref38). 문장 쌍은 대략적인 sequence 길이에 따라 함께 배치되었습니다. 각 훈련 배치에는 약 25,000개의 소스 토큰과 25,000개의 타겟 토큰을 포함하는 문장 쌍 집합이 포함되었습니다.

### 5.2 하드웨어 및 일정

우리는 8개의 NVIDIA P100 GPU가 장착된 한 대의 머신에서 model을 훈련했습니다. 논문 전체에서 설명된 하이퍼파라미터를 사용하는 기본 model의 경우, 각 훈련 단계는 약 0.4초가 걸렸습니다. 우리는 기본 model을 총 100,000 단계 또는 12시간 동안 훈련했습니다. 우리의 큰 model(표 3의 맨 아래 줄에 설명됨)의 경우, 단계 시간은 1.0초였습니다. 큰 model은 300,000 단계(3.5일) 동안 훈련되었습니다.

### 5.3 Optimizer

우리는 $\beta_1 = 0.9$, $\beta_2 = 0.98$, $\epsilon = 10^{-9}$인 Adam optimizer [20](#ref20)를 사용했습니다. 우리는 훈련 과정 동안 다음 공식에 따라 학습률을 변경했습니다:

$$
lrate = d_{\text{model}}^{-0.5} \cdot \min(\text{step\_num}^{-0.5}, \text{step\_num} \cdot \text{warmup\_steps}^{-1.5})
$$

이는 첫 `warmup_steps` 훈련 단계 동안 학습률을 선형적으로 증가시키고, 그 이후에는 단계 수의 역제곱근에 비례하여 감소시키는 것에 해당합니다. 우리는 `warmup_steps = 4000`을 사용했습니다.

### 5.4 정규화

우리는 훈련 중에 세 가지 유형의 정규화를 사용합니다:

**Residual Dropout** 우리는 각 sub-layer의 출력에 dropout [33](#ref33]을 적용한 후, sub-layer 입력에 더하고 정규화합니다. 또한, encoder와 decoder 스택 모두에서 embedding과 positional encoding의 합에 dropout을 적용합니다. 기본 model의 경우, 우리는 $P_{drop} = 0.1$의 비율을 사용합니다.

**Label Smoothing** 훈련 중에, 우리는 값 $\epsilon_{ls} = 0.1$의 label smoothing을 사용했습니다 [36](#ref36]. 이는 model이 더 불확실하게 학습하게 되므로 perplexity를 손상시키지만, 정확도와 BLEU 점수를 향상시킵니다.

## 6. 결과

### 6.1 기계 번역

WMT 2014 영어-독일어 번역 과제에서, 큰 transformer model(Table 2의 Transformer (big))은 이전에 보고된 최고의 model(앙상블 포함)을 2.0 BLEU 이상 능가하여 28.4라는 새로운 state-of-the-art BLEU 점수를 기록했습니다. 이 model의 구성은 Table 3의 맨 아래 줄에 나열되어 있습니다. 훈련은 8개의 P100 GPU에서 3.5일이 걸렸습니다. 우리의 기본 model조차도 이전에 발표된 모든 model과 앙상블을 능가하며, 경쟁 model의 훈련 비용의 일부만으로도 가능합니다.

WMT 2014 영어-프랑스어 번역 과제에서, 우리의 큰 model은 41.8의 BLEU 점수를 달성하여, 이전 state-of-the-art model의 훈련 비용의 1/4 미만으로 이전에 발표된 모든 단일 model을 능가했습니다. 영어-프랑스어용으로 훈련된 Transformer (big) model은 $P_{drop} = 0.3$ 대신 $0.1$의 dropout 비율을 사용했습니다.

기본 model의 경우, 우리는 10분 간격으로 작성된 마지막 5개의 체크포인트를 평균하여 얻은 단일 model을 사용했습니다. 큰 model의 경우, 우리는 마지막 20개의 체크포인트를 평균했습니다. 우리는 빔 크기 4와 길이 페널티 $\alpha = 0.6$을 사용한 빔 검색을 사용했습니다 [38](#ref38). 이러한 하이퍼파라미터는 개발 세트에서 실험 후 선택되었습니다. 우리는 추론 중 최대 출력 길이를 입력 길이 + 50으로 설정했지만, 가능할 때 조기 종료했습니다 [38](#ref38).

Table 2는 우리의 결과를 요약하고 우리의 번역 품질과 훈련 비용을 문헌의 다른 model 아키텍처와 비교합니다. 우리는 훈련 시간, 사용된 GPU 수, 각 GPU의 지속적인 단일 정밀도 부동 소수점 용량 추정치를 곱하여 model을 훈련하는 데 사용된 부동 소수점 연산 수를 추정합니다.

| Model | BLEU (EN-DE) | BLEU (EN-FR) | Training Cost (FLOPs) |
| :--- | :--- | :--- | :--- |
| ByteNet [18](#ref18) | 23.75 | | | 
| Deep-Att + PosUnk [39](#ref39) | | 39.2 | | 1.0 \cdot 10²⁰ |
| GNMT + RL [38](#ref38) | 24.6 | 39.92 | 2.3 \cdot 10¹⁹ | 1.4 \cdot 10²⁰ |
| ConvS2S [9](#ref9) | 25.16 | 40.46 | 9.6 \cdot 10¹⁸ | 1.5 \cdot 10²⁰ |
| MoE [32](#ref32) | 26.03 | 40.56 | 2.0 \cdot 10¹⁹ | 1.2 \cdot 10²⁰ |
| Deep-Att + PosUnk Ensemble [39](#ref39) | | 40.4 | | 8.0 \cdot 10²⁰ |
| GNMT + RL Ensemble [38](#ref38) | 26.30 | 41.16 | 1.8 \cdot 10²⁰ | 1.1 \cdot 10²¹ |
| ConvS2S Ensemble [9](#ref9) | 26.36 | 41.29 | 7.7 \cdot 10¹⁹ | 1.2 \cdot 10²¹ |
| **Transformer (base model)** | **27.3** | **38.1** | **3.3 \cdot 10¹⁸** | | 
| **Transformer (big)** | **28.4** | **41.8** | **2.3 \cdot 10¹⁹** | | 
<p align="center">Table 2: Transformer는 이전 state-of-the-art model보다 더 나은 BLEU 점수를 영어-독일어 및 영어-프랑스어 newstest2014 테스트에서 훈련 비용의 일부만으로 달성합니다.</p>

### 6.2 Model Variations

Transformer의 다른 구성 요소의 중요성을 평가하기 위해, 우리는 기본 model을 다양한 방식으로 변경하여 영어-독일어 번역의 개발 세트인 newstest2013에서 성능 변화를 측정했습니다. 우리는 이전 섹션에서 설명한 빔 검색을 사용했지만 체크포인트 평균화는 사용하지 않았습니다. 우리는 이러한 결과를 Table 3에 제시합니다.

Table 3 행 (A)에서, 우리는 attention head의 수와 attention key 및 value 차원을 변경하면서, 섹션 3.2.2에서 설명한 대로 계산량을 일정하게 유지합니다. 단일 head attention은 최상의 설정보다 0.9 BLEU 더 나쁘지만, head가 너무 많아도 품질이 떨어집니다.

Table 3 행 (B)에서, 우리는 attention key 크기 $d_k$를 줄이면 model 품질이 저하됨을 관찰합니다. 이는 호환성을 결정하는 것이 쉽지 않으며 dot product보다 더 정교한 호환성 함수가 유익할 수 있음을 시사합니다. 우리는 행 (C)와 (D)에서 예상대로 더 큰 model이 더 좋고, dropout이 과적합을 피하는 데 매우 도움이 된다는 것을 추가로 관찰합니다. 행 (E)에서는 사인파 positional encoding을 학습된 positional embedding [9](#ref9)으로 대체하고 기본 model과 거의 동일한 결과를 관찰합니다.

| | N | $d_{\text{model}}$ | $d_{ff}$ | h | $d_k$ | $d_v$ | $P_{drop}$ | $\epsilon_{ls}$ | train steps | PPL (dev) | BLEU (dev) | params $\times 10^6$ |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| base | 6 | 512 | 2048 | 8 | 64 | 64 | 0.1 | 0.1 | 100K | 4.92 | 25.8 | 65 |
| (A) | | | | 1 | 512 | 512 | | | | 5.29 | 24.9 | | 
| | | | | 4 | 128 | 128 | | | | 5.00 | 25.5 | | 
| | | | | 16 | 32 | 32 | | | | 4.91 | 25.8 | | 
| | | | | 32 | 16 | 16 | | | | 5.01 | 25.4 | | 
| (B) | | | | | 16 | | | | | 5.16 | 25.1 | 58 |
| | | | | | 32 | | | | | 5.01 | 25.4 | 60 |
| (C) | 2 | | | | | | | | | 6.11 | 23.7 | 36 |
| | 4 | | | | | | | | | 5.19 | 25.3 | 50 |
| | 8 | | | | | | | | | 4.88 | 25.5 | 80 |
| | | 256 | | | 32 | 32 | | | | 5.75 | 24.5 | 28 |
| | | 1024 | | | 128 | 128 | | | | 4.66 | 26.0 | 168 |
| | | | 1024 | | | | | | | 5.12 | 25.4 | 53 |
| | | | 4096 | | | | | | | 4.75 | 26.2 | 90 |
| (D) | | | | | | | 0.0 | | | 5.77 | 24.6 | | 
| | | | | | | | 0.2 | | | 4.95 | 25.5 | | 
| | | | | | | | | 0.0 | | 4.67 | 25.3 | | 
| | | | | | | | | 0.2 | | 5.47 | 25.7 | | 
| (E) | | | | | | | | | | 4.92 | 25.7 | | 
| | \multicolumn{8}{c|}{positional embedding instead of sinusoids} | | | | | 
| big | 6 | 1024 | 4096 | 16 | | | 0.3 | | 300K | 4.33 | 26.4 | 213 |
<p align="center">Table 3: Transformer 아키텍처의 변형. 나열되지 않은 값은 기본 model의 값과 동일합니다. 모든 메트릭은 영어-독일어 번역 개발 세트, newstest2013에 대한 것입니다. 나열된 perplexity는 우리의 byte-pair 인코딩에 따른 단어 조각당 perplexity이며, 단어당 perplexity와 비교해서는 안 됩니다.</p>

### 6.3 English Constituency Parsing

Transformer가 다른 과제에 일반화될 수 있는지 평가하기 위해, 우리는 영어 구문 분석에 대한 실험을 수행했습니다. 이 과제는 특정한 어려움을 제시합니다: 출력은 강력한 구조적 제약을 받으며 입력보다 훨씬 깁니다. 또한, RNN sequence-to-sequence model은 소규모 데이터 체제에서 state-of-the-art 결과를 달성하지 못했습니다 [37](#ref37).

우리는 Penn Treebank [25](#ref25)의 Wall Street Journal (WSJ) 부분, 약 40K 훈련 문장에 대해 $d_{\text{model}} = 1024$인 4-layer transformer를 훈련했습니다. 또한 약 1,700만 개의 문장을 가진 더 큰 고신뢰도 및 BerkleyParser 코퍼스를 사용하여 반지도 학습 환경에서도 훈련했습니다 [37](#ref37]. WSJ 전용 설정에는 16K 토큰의 어휘를, 반지도 학습 설정에는 32K 토큰의 어휘를 사용했습니다.

우리는 섹션 22 개발 세트에서 dropout, attention 및 residual (섹션 5.4), 학습률 및 빔 크기를 선택하기 위해 소수의 실험만 수행했으며, 다른 모든 파라미터는 영어-독일어 기본 번역 model에서 변경되지 않았습니다. 추론 중에, 우리는 최대 출력 길이를 입력 길이 + 300으로 늘렸습니다. 우리는 WSJ 전용 및 반지도 학습 설정 모두에 대해 빔 크기 21과 $\alpha = 0.3$을 사용했습니다.

Table 4의 우리 결과는 과제별 튜닝이 부족함에도 불구하고 우리 model이 놀랍게도 잘 수행되어, Recurrent Neural Network Grammar [8](#ref8)를 제외한 모든 이전에 보고된 model보다 더 나은 결과를 산출함을 보여줍니다.

RNN sequence-to-sequence model [37](#ref37]과 대조적으로, Transformer는 단 40K 문장의 WSJ 훈련 세트에서만 훈련했을 때도 BerkeleyParser [29](#ref29)를 능가합니다.

| Parser | Training | WSJ 23 F1 |
| :--- | :--- | :--- |
| Vinyals & Kaiser et al. (2014) [37](#ref37) | WSJ only, discriminative | 88.3 |
| Petrov et al. (2006) [29](#ref29) | WSJ only, discriminative | 90.4 |
| Zhu et al. (2013) [40](#ref40) | WSJ only, discriminative | 90.4 |
| Dyer et al. (2016) [8](#ref8) | WSJ only, discriminative | 91.7 |
| **Transformer (4 layers)** | **WSJ only, discriminative** | **91.3** |
| Zhu et al. (2013) [40](#ref40) | semi-supervised | 91.3 |
| Huang & Harper (2009) [14](#ref14) | semi-supervised | 91.3 |
| McClosky et al. (2006) [26](#ref26) | semi-supervised | 92.1 |
| Vinyals & Kaiser et al. (2014) [37](#ref37) | semi-supervised | 92.1 |
| **Transformer (4 layers)** | **semi-supervised** | **92.7** |
| Luong et al. (2015) [23](#ref23) | multi-task | 93.0 |
| Dyer et al. (2016) [8](#ref8) | generative | 93.3 |
<p align="center">Table 4: Transformer는 영어 구문 분석에도 잘 일반화됩니다 (결과는 WSJ의 섹션 23에 대한 것입니다).</p>

## 7. 결론

이 연구에서, 우리는 encoder-decoder 아키텍처에서 가장 일반적으로 사용되는 recurrent layer를 multi-headed self-attention으로 대체하여, 전적으로 attention에 기반한 최초의 sequence transduction model인 Transformer를 제시했습니다.

번역 과제의 경우, Transformer는 recurrent 또는 convolutional layer에 기반한 아키텍처보다 훨씬 빠르게 훈련될 수 있습니다. WMT 2014 영어-독일어 및 WMT 2014 영어-프랑스어 번역 과제 모두에서, 우리는 새로운 state-of-the-art를 달성합니다. 이전 과제에서 우리의 최고 model은 이전에 보고된 모든 앙상블조차도 능가합니다.

우리는 attention 기반 model의 미래에 대해 흥분하고 있으며 다른 과제에 적용할 계획입니다. 우리는 Transformer를 텍스트 이외의 입출력 양식을 포함하는 문제로 확장하고, 이미지, 오디오, 비디오와 같은 대규모 입출력을 효율적으로 처리하기 위해 지역적, 제한된 attention 메커니즘을 조사할 계획입니다. 생성을 덜 순차적으로 만드는 것이 우리의 또 다른 연구 목표입니다.

우리가 모델을 훈련하고 평가하는 데 사용한 코드는 [https://github.com/tensorflow/tensor2tensor](https://github.com/tensorflow/tensor2tensor)에서 사용할 수 있습니다.

**감사의 말** 우리는 Nal Kalchbrenner와 Stephan Gouws에게 유익한 의견, 수정 및 영감을 준 것에 대해 감사합니다.

## 참고문헌

- <a id="ref1"></a>[1] Jimmy Lei Ba, Jamie Ryan Kiros, and Geoffrey E Hinton. Layer normalization. arXiv preprint arXiv:1607.06450, 2016.
- <a id="ref2"></a>[2] Dzmitry Bahdanau, Kyunghyun Cho, and Yoshua Bengio. Neural machine translation by jointly learning to align and translate. CoRR, abs/1409.0473, 2014.
- <a id="ref3"></a>[3] Denny Britz, Anna Goldie, Minh-Thang Luong, and Quoc V. Le. Massive exploration of neural machine translation architectures. CoRR, abs/1703.03906, 2017.
- <a id="ref4"></a>[4] Jianpeng Cheng, Li Dong, and Mirella Lapata. Long short-term memory-networks for machine reading. arXiv preprint arXiv:1601.06733, 2016.
- <a id="ref5"></a>[2] Kyunghyun Cho, Bart van Merrienboer, Caglar Gulcehre, Fethi Bougares, Holger Schwenk, and Yoshua Bengio. Learning phrase representations using rnn encoder-decoder for statistical machine translation. CoRR, abs/1406.1078, 2014.
- <a id="ref6"></a>[6] Francois Chollet. Xception: Deep learning with depthwise separable convolutions. arXiv preprint arXiv:1610.02357, 2016.
- <a id="ref7"></a>[7] Junyoung Chung, Çaglar Gülçehre, Kyunghyun Cho, and Yoshua Bengio. Empirical evaluation of gated recurrent neural networks on sequence modeling. CoRR, abs/1412.3555, 2014.
- <a id="ref8"></a>[8] Chris Dyer, Adhiguna Kuncoro, Miguel Ballesteros, and Noah A. Smith. Recurrent neural network grammars. In Proc. of NAACL, 2016.
- <a id="ref9"></a>[9] Jonas Gehring, Michael Auli, David Grangier, Denis Yarats, and Yann N. Dauphin. Convolutional sequence to sequence learning. arXiv preprint arXiv:1705.03122v2, 2017.
- <a id="ref10"></a>[10] Alex Graves. Generating sequences with recurrent neural networks. arXiv preprint arXiv:1308.0850, 2013.
- <a id="ref11"></a>[11] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. Deep residual learning for image recognition. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition, pages 770–778, 2016.
- <a id="ref12"></a>[12] Sepp Hochreiter, Yoshua Bengio, Paolo Frasconi, and Jürgen Schmidhuber. Gradient flow in recurrent nets: the difficulty of learning long-term dependencies, 2001.
- <a id="ref13"></a>[13] Sepp Hochreiter and Jürgen Schmidhuber. Long short-term memory. Neural computation, 9(8):1735–1780, 1997.
- <a id="ref14"></a>[14] Zhongqiang Huang and Mary Harper. Self-training PCFG grammars with latent annotations across languages. In Proceedings of the 2009 Conference on Empirical Methods in Natural Language Processing, pages 832–841. ACL, August 2009.
- <a id="ref15"></a>[15] Rafal Jozefowicz, Oriol Vinyals, Mike Schuster, Noam Shazeer, and Yonghui Wu. Exploring the limits of language modeling. arXiv preprint arXiv:1602.02410, 2016.
- <a id="ref16"></a>[16] Łukasz Kaiser and Samy Bengio. Can active memory replace attention? In Advances in Neural Information Processing Systems, (NIPS), 2016.
- <a id="ref17"></a>[17] Łukasz Kaiser and Ilya Sutskever. Neural GPUs learn algorithms. In International Conference on Learning Representations (ICLR), 2016.
- <a id="ref18"></a>[18] Nal Kalchbrenner, Lasse Espeholt, Karen Simonyan, Aaron van den Oord, Alex Graves, and Koray Kavukcuoglu. Neural machine translation in linear time. arXiv preprint arXiv:1610.10099v2, 2017.
- <a id="ref19"></a>[19] Yoon Kim, Carl Denton, Luong Hoang, and Alexander M. Rush. Structured attention networks. In International Conference on Learning Representations, 2017.
- <a id="ref20"></a>[20] Diederik Kingma and Jimmy Ba. Adam: A method for stochastic optimization. In ICLR, 2015.
- <a id="ref21"></a>[21] Oleksii Kuchaiev and Boris Ginsburg. Factorization tricks for LSTM networks. arXiv preprint arXiv:1703.10722, 2017.
- <a id="ref22"></a>[22] Zhouhan Lin, Minwei Feng, Cicero Nogueira dos Santos, Mo Yu, Bing Xiang, Bowen Zhou, and Yoshua Bengio. A structured self-attentive sentence embedding. arXiv preprint arXiv:1703.03130, 2017.
- <a id="ref23"></a>[23] Minh-Thang Luong, Quoc V. Le, Ilya Sutskever, Oriol Vinyals, and Lukasz Kaiser. Multi-task sequence to sequence learning. arXiv preprint arXiv:1511.06114, 2015.
- <a id="ref24"></a>[24] Minh-Thang Luong, Hieu Pham, and Christopher D Manning. Effective approaches to attention-based neural machine translation. arXiv preprint arXiv:1508.04025, 2015.
- <a id="ref25"></a>[25] Mitchell P Marcus, Mary Ann Marcinkiewicz, and Beatrice Santorini. Building a large annotated corpus of english: The penn treebank. Computational linguistics, 19(2):313–330, 1993.
- <a id="ref26"></a>[26] David McClosky, Eugene Charniak, and Mark Johnson. Effective self-training for parsing. In Proceedings of the Human Language Technology Conference of the NAACL, Main Conference, pages 152–159. ACL, June 2006.
- <a id="ref27"></a>[27] Ankur Parikh, Oscar Täckström, Dipanjan Das, and Jakob Uszkoreit. A decomposable attention model. In Empirical Methods in Natural Language Processing, 2016.
- <a id="ref28"></a>[28] Romain Paulus, Caiming Xiong, and Richard Socher. A deep reinforced model for abstractive summarization. arXiv preprint arXiv:1705.04304, 2017.
- <a id="ref29"></a>[29] Slav Petrov, Leon Barrett, Romain Thibaux, and Dan Klein. Learning accurate, compact, and interpretable tree annotation. In Proceedings of the 21st International Conference on Computational Linguistics and 44th Annual Meeting of the ACL, pages 433–440. ACL, July 2006.
- <a id="ref30"></a>[30] Ofir Press and Lior Wolf. Using the output embedding to improve language models. arXiv preprint arXiv:1608.05859, 2016.
- <a id="ref31"></a>[31] Rico Sennrich, Barry Haddow, and Alexandra Birch. Neural machine translation of rare words with subword units. arXiv preprint arXiv:1508.07909, 2015.
- <a id="ref32"></a>[32] Noam Shazeer, Azalia Mirhoseini, Krzysztof Maziarz, Andy Davis, Quoc Le, Geoffrey Hinton, and Jeff Dean. Outrageously large neural networks: The sparsely-gated mixture-of-experts layer. arXiv preprint arXiv:1701.06538, 2017.
- <a id="ref33"></a>[33] Nitish Srivastava, Geoffrey E Hinton, Alex Krizhevsky, Ilya Sutskever, and Ruslan Salakhutdinov. Dropout: a simple way to prevent neural networks from overfitting. Journal of Machine Learning Research, 15(1):1929–1958, 2014.
- <a id="ref34"></a>[34] Sainbayar Sukhbaatar, Arthur Szlam, Jason Weston, and Rob Fergus. End-to-end memory networks. In C. Cortes, N. D. Lawrence, D. D. Lee, M. Sugiyama, and R. Garnett, editors, Advances in Neural Information Processing Systems 28, pages 2440–2448. Curran Associates, Inc., 2015.
- <a id="ref35"></a>[35] Ilya Sutskever, Oriol Vinyals, and Quoc VV Le. Sequence to sequence learning with neural networks. In Advances in Neural Information Processing Systems, pages 3104–3112, 2014.
- <a id="ref36"></a>[36] Christian Szegedy, Vincent Vanhoucke, Sergey Ioffe, Jonathon Shlens, and Zbigniew Wojna. Rethinking the inception architecture for computer vision. CoRR, abs/1512.00567, 2015.
- <a id="ref37"></a>[37] Vinyals & Kaiser, Koo, Petrov, Sutskever, and Hinton. Grammar as a foreign language. In Advances in Neural Information Processing Systems, 2015.
- <a id="ref38"></a>[38] Yonghui Wu, Mike Schuster, Zhifeng Chen, Quoc V Le, Mohammad Norouzi, Wolfgang Macherey, Maxim Krikun, Yuan Cao, Qin Gao, Klaus Macherey, et al. Google’s neural machine translation system: Bridging the gap between human and machine translation. arXiv preprint arXiv:1609.08144, 2016.
- <a id="ref39"></a>[39] Jie Zhou, Ying Cao, Xuguang Wang, Peng Li, and Wei Xu. Deep recurrent models with fast-forward connections for neural machine translation. CoRR, abs/1606.04199, 2016.
- <a id="ref40"></a>[40] Muhua Zhu, Yue Zhang, Wenliang Chen, Min Zhang, and Jingbo Zhu. Fast and accurate shift-reduce constituent parsing. In Proceedings of the 51st Annual Meeting of the ACL (Volume 1: Long Papers), pages 434–443. ACL, August 2013.

## 부록

<figure>
    <img src="assets/figure_3.png" alt="Figure 3">
    <figcaption><p>Figure 3: An example of the attention mechanism following long-distance dependencies in the encoder self-attention in layer 5 of 6. Many of the attention heads attend to a distant dependency of the verb 'making', completing the phrase 'making...more difficult'. Attentions here shown only for the word 'making'. Different colors represent different heads. Best viewed in color.</p></figcaption>
</figure>

<figure>
    <img src="assets/figure_4.png" alt="Figure 4">
    <figcaption><p>Figure 4: Two attention heads, also in layer 5 of 6, apparently involved in anaphora resolution. Top: Full attentions for head 5. Bottom: Isolated attentions from just the word 'its' for attention heads 5 and 6. Note that the attentions are very sharp for this word.</p></figcaption>
</figure>

<figure>
    <img src="assets/figure_5.png" alt="Figure 5">
    <figcaption><p>Figure 5: Many of the attention heads exhibit behaviour that seems related to the structure of the sentence. We give two such examples above, from two different heads from the encoder self-attention at layer 5 of 6. The heads clearly learned to perform different tasks.</p></figcaption>
</figure>
