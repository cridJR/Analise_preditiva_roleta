import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# Caminhos baseados na sua estrutura de pastas
DATASET_PATH = "intelligence_data/roulette_dataset.csv"
MODEL_DIR = "intelligence_data"
MODEL_NAME = "trained_model.pkl"

def train_engine():
    # 1. Verificação de Segurança (SRE style)
    if not os.path.exists(DATASET_PATH):
        print(f"❌ Erro: Dataset não encontrado em {DATASET_PATH}")
        return

    print("📊 Carregando dados para treinamento...")
    df = pd.read_csv(DATASET_PATH)

    if len(df) < 20:
        print(f"⚠️ Amostra muito pequena ({len(df)} giros). Insira mais dados para melhor precisão.")
        return

    # 2. Engenharia de Features
    # Vamos ensinar a IA a prever o PRÓXIMO setor baseado no ATUAL
    df['proximo_setor'] = df['setor'].shift(-1)
    
    # Removemos a última linha pois não sabemos o "próximo" dela ainda
    dataset_final = df.dropna().copy()

    # 3. Transformação de Texto para Número (Label Encoding)
    le_setor = LabelEncoder()
    le_cor = LabelEncoder()

    # Precisamos encodar os setores e as cores para que o algoritmo entenda
    dataset_final['setor_encoded'] = le_setor.fit_transform(dataset_final['setor'])
    dataset_final['cor_encoded'] = le_cor.fit_transform(dataset_final['cor'])
    dataset_final['target'] = le_setor.transform(dataset_final['proximo_setor'])

    # 4. Definição das variáveis de entrada (Features) e saída (Target)
    X = dataset_final[['setor_encoded', 'cor_encoded', 'duzia', 'coluna']]
    y = dataset_final['target']

    # 5. Treinamento com Random Forest
    print("🧠 Treinando o modelo Random Forest...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    # 6. Persistência do Modelo
    os.makedirs(MODEL_DIR, exist_ok=True)
    full_path = os.path.join(MODEL_DIR, MODEL_NAME)
    
    # Salvamos o modelo e os encodings para podermos "traduzir" de volta depois
    joblib.dump({
        'model': model,
        'le_setor': le_setor,
        'le_cor': le_cor
    }, full_path)

    print(f"✅ Sucesso! Modelo salvo em: {full_path}")
    print(f"📈 Total de giros analisados: {len(dataset_final)}")

if __name__ == "__main__":
    train_engine()