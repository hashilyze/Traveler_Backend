import torch
import torch.nn as nn

import numpy as np

import pandas as pd
import scipy.sparse as sp
import torch.utils.data as data

# data path
root_path = 'BPR'
train_checkin = root_path + '/Data/train.csv'
test_checkin = root_path + '/Data/test.csv'
test_negative = root_path + '/Data/negative.csv'

# 하드코딩된 기본값 설정
lr = 0.001
lamda = 0.001
batch_size = 4096
epochs = 10
top_k = 10
num_factors = 32
num_ng = 4
test_num_ng = 99
out = True


class BPRData(data.Dataset):
    def __init__(self, features, num_item, train_mat=None, num_ng=0, is_training=None):
        super(BPRData, self).__init__()
        self.features = features # train_data
        self.num_item = num_item # 아이템 수
        self.train_mat = train_mat # 훈련 데이터의 희소 행렬
        self.num_ng = num_ng # 부정적 샘플의 수
        self.is_training = is_training # 훈련모드의 여부

    def ng_sample(self): # 부정적 샘플링
        assert self.is_training, 'no need to sampling when testing'

        self.features_fill = []
        for x in self.features:
            u, i = x[0], x[1]
            for t in range(self.num_ng):
                j = np.random.randint(self.num_item)
                while (u, j) in self.train_mat: #train_mat를 사용하여 (u,j)라는 특정 사용자-아이템 쌍이 train_data에 존재하는지 여부를 빠르게 확인함.
                    j = np.random.randint(self.num_item) # (u,j)가 희소행렬에 존재 한다면 방문하지 않은 음식점 j를 찾을 때까지 랜덤값으로 값 획득
                self.features_fill.append([u, i, j]) #triple_data를 획득

    def __len__(self):
        if self.is_training:
            return self.num_ng * len(self.features)
        else:
            return len(self.features)

    def __getitem__(self, idx):
        features = self.features_fill if self.is_training else self.features

        user = features[idx][0]
        item_i = features[idx][1]
        item_j = features[idx][2] if self.is_training else features[idx][1]
        return user, item_i, item_j


class BPR(nn.Module):
    def __init__(self, num_users, num_items, num_factors=10):
        super(BPR, self).__init__()
        self.user_factors = nn.Embedding(num_users, num_factors) # 초기 임베딩값을 무작위로 넣는게 사전확률로 볼 수 있다.
        self.item_factors = nn.Embedding(num_items, num_factors)

    def forward(self, user_ids, item_ids_i, item_ids_j):
      user_embedding = self.user_factors(user_ids) # # 파라미터 p(u)
      item_embedding_i = self.item_factors(item_ids_i) #파라미터 q(i)
      item_embedding_j = self.item_factors(item_ids_j)# 파라미터 q(j)

      # 내적을 통한 예측값 계산

      #x(uij)를 구하기 위한과정
      pred_i = torch.sum(user_embedding * item_embedding_i, dim=-1)  #아이템 i에 대한 점수 x(ui) -> p(u)*(q(i)^T)
      pred_j = torch.sum(user_embedding * item_embedding_j, dim=-1) #아이템 j에 대한 점수 x(uj)  -> p(u)*(q(j)^T)

      return pred_i, pred_j


def load_all():
    # 학습 데이터 로드
    train_data = pd.read_csv(
        train_checkin,
        sep='\t', header=None, names=['user', 'item'],
        usecols=[0, 1], dtype={0: np.int32, 1: np.int32})


    # 사용자 및 아이템 수 계산
    user_num = train_data['user'].max() + 1
    item_num = train_data['item'].max() + 1

    # 학습 데이터를 리스트로 변환
    train_data = train_data.values.tolist()

    # 학습 데이터를 scipy sparse matrix로 변환
    train_mat = sp.dok_matrix((user_num, item_num), dtype=np.float32) # 희소 행렬은 메모리 사용량을 줄이고, 특정 요소에 대한 빠른 조회를 가능하게 함.
    for x in train_data: #후속 단계에서 부정적 샘플링을 수행할 때 유용
        train_mat[x[0], x[1]] = 1.0 # 사용자와 음식점의 쌍이 존재한다는것을 알리기 위해 1.0 표시

    # 테스트 데이터 로드
    test_data = []
    with open(test_negative, 'r') as fd:
        line = fd.readline()
        while line != None and line != '':
            arr = line.split('\t') # test_negative를 \t를 기준 형식에 맞추기
            u = eval(arr[0])[0] # 사용자 n
            test_data.append([u, eval(arr[0])[1]]) #방문한 음식점 추가
            for i in arr[1:]:
                test_data.append([u, int(i)]) #방문하지 않은 음식점 추가
            line = fd.readline()

    return train_data, test_data, user_num, item_num, train_mat


################# DATASET 준비 ##################
train_data, test_data, user_num ,item_num, train_mat = load_all()

train_dataset = BPRData(train_data, item_num, train_mat, num_ng, True)
test_dataset = BPRData(test_data, item_num, train_mat, 0, False)

train_loader = data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
test_loader = data.DataLoader(test_dataset, batch_size=test_num_ng+1, shuffle=False, num_workers=0)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = BPR(user_num, item_num, num_factors)
model.to(device)
model.load_state_dict(torch.load(root_path + '/Model/BPR.pt', map_location=torch.device('cpu'), weights_only=True))
model.eval()


#def recommend_restaurants(user_id, model, train_mat, item_num, top_k=10):
def recommend_restaurants(user_id, top_k=10):
    """
    Arg:
    - user_id (int): 추천을 받을 사용자 ID.
    - model (torch.nn.Module): 학습된 BPR 모델.
    - train_mat (scipy.sparse.dok_matrix): 사용자-아이템 희소 행렬, 이미 방문한 음식점 확인에 사용
    - item_num (int): 전체 아이템(음식점) 수.
    - top_k (int): 추천받을 음식점의 수.

    Returns:
    - top_k_items (list of int): 추천된 상위 음식점 ID 리스트.
    """
    # 모든 아이템(음식점)을 대상으로 평가
    item_ids = torch.tensor(range(item_num)).to(device)

    # 사용자 임베딩과 아이템 임베딩을 계산
    user_embedding = model.user_factors(torch.tensor([user_id]).to(device))
    item_embeddings = model.item_factors(item_ids)

    # 내적(matmul)을 통해 각 음식점에 대한 점수 산출 ( [user_embedding * d] [d* item_embeddings] ) ".t()"를 통해 전치행렬로 변환
    # squeeze(0)을 통해 1차원 벡터로 변환 / cpu() - GPU에 있는 텐서를 CPU로 옮김
    scores = torch.matmul(user_embedding, item_embeddings.t()).squeeze(0).cpu().detach().numpy()

    # 이미 방문한 음식점은 추천에서 제외
    # print(train_mat[user_id].keys())
    already_visited = list(train_mat[user_id].keys())
    for visited_item in already_visited:
        scores[visited_item[1]] = -np.inf  # 이미 방문한 음식점의 점수를 -무한대로 설정

    # 상위 top_k 음식점을 추출
    top_k_items = np.argsort(scores)[-top_k:][::-1]  # 점수가 높은 순서대로 정렬

    return top_k_items


if __name__ == '__main__':
    # 사용자 n에 대해 상위 10개 음식점을 추천
    user_id = 3789  # 추천할 사용자 ID
    #top_k_items = recommend_restaurants(user_id, model, train_mat, item_num, top_k=10)
    top_k_items = recommend_restaurants(user_id)

    print(f"Top {len(top_k_items)} 추천 음식점 for 사용자 {user_id}: {top_k_items}")