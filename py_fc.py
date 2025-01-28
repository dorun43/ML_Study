import pandas as pd
import numpy as np
import torch
from pytorch_forecasting import TimeSeriesDataSet, TemporalFusionTransformer, Baseline
from pytorch_forecasting.data import GroupNormalizer
from pytorch_forecasting.metrics import QuantileLoss
from pytorch_lightning import Trainer

# 1. 데이터 준비
# 가상의 코스피 200 분봉 데이터 생성 (실제 데이터로 교체 가능)
np.random.seed(42)
dates = pd.date_range("2023-01-01", periods=1000, freq="T")
data = pd.DataFrame({
    "time_idx": np.arange(len(dates)),  # 시계열 인덱스
    "date": dates.date,
    "종가": np.random.rand(1000) * 100 + 2500,  # 종가
    "시가": np.random.rand(1000) * 100 + 2500,  # 시가
    "고가": np.random.rand(1000) * 100 + 2550,  # 고가
    "저가": np.random.rand(1000) * 100 + 2450,  # 저가
    "거래량": np.random.randint(100, 1000, size=1000),  # 거래량
    "group": "0"  # 단일 그룹
})

# 2. TimeSeriesDataSet 설정
max_encoder_length = 30  # 과거 데이터를 바라볼 윈도우 크기
max_prediction_length = 10  # 예측할 미래 데이터 개수

dataset = TimeSeriesDataSet(
    data,
    time_idx="time_idx",
    target="종가",
    group_ids=["group"],
    min_encoder_length=max_encoder_length // 2,  # 최소 입력 길이
    max_encoder_length=max_encoder_length,  # 최대 입력 길이
    min_prediction_length=1,
    max_prediction_length=max_prediction_length,  # 예측 길이
    static_categoricals=["group"],
    time_varying_known_reals=["time_idx", "시가", "고가", "저가", "거래량"],  # 알려진 실수형 변수
    time_varying_unknown_reals=["종가"],  # 예측 대상
    target_normalizer=GroupNormalizer(transformation="softplus"),  # 종가 정규화
    add_relative_time_idx=True,
    add_target_scales=True,
)

# 3. 데이터 로더 생성
train_dataloader = dataset.to_dataloader(train=True, batch_size=64, num_workers=0)
val_dataloader = dataset.to_dataloader(train=False, batch_size=64, num_workers=0)

# 4. 모델 정의
tft = TemporalFusionTransformer.from_dataset(
    dataset,
    learning_rate=1e-3,
    hidden_size=16,  # 모델의 크기
    attention_head_size=1,
    dropout=0.1,
    hidden_continuous_size=8,
    output_size=7,  # 7개의 퀀타일 (0.1, 0.2, ..., 0.9)
    loss=QuantileLoss(),
    log_interval=10,  # 로깅 빈도
    reduce_on_plateau_patience=4,  # 학습률 감소 기준
)

# 5. 모델 학습
trainer = Trainer(
    max_epochs=30,
    #gpus=1 if torch.cuda.is_available() else 0,
    gradient_clip_val=0.1,
)

trainer.fit(
    tft,
    train_dataloaders=train_dataloader,
    val_dataloaders=val_dataloader,
)

# 6. 모델 예측
# 새로운 데이터를 사용해 예측
raw_predictions, x = tft.predict(val_dataloader, mode="raw", return_x=True)

# 예측값 시각화
tft.plot_prediction(x, raw_predictions, idx=0)
