import { useState, useEffect } from 'react';

// Tipagem corrigida para coincidir com o mapear_dados do backend
interface RegistroGiro {
  numero: number;
  cor: string;
  paridade: string;
  duzia: number;
}

interface Sugestao {
  analise: {
    V: number;
    P: number;
  };
  sugestao: string;
  mensagem?: string; 
}

function App() {
  // Inicialização segura para evitar o erro 'map of undefined'
  const [historico, setHistorico] = useState<RegistroGiro[]>([]);
  const [sugestao, setSugestao] = useState<Sugestao | null>(null);

  const fetchDados = async () => {
    try {
      // Busca o histórico diretamente da rota do backend
      const resHist = await fetch('http://localhost:8000/historico');
      const dataHist = await resHist.json();
      setHistorico(Array.isArray(dataHist) ? dataHist : []);

      const resSug = await fetch('http://localhost:8000/sugestao');
      const dataSug = await resSug.json();
      setSugestao(dataSug);
    } catch (err) {
      console.error("Erro ao conectar com a API:", err);
    }
  };

  // Função para resetar o Redis através da nova API DELETE
  const resetarDados = async () => {
    if (window.confirm("Deseja realmente limpar todo o histórico do Redis?")) {
      try {
        const response = await fetch('http://localhost:8000/limpar-historico', {
          method: 'DELETE',
        });
        
        if (response.ok) {
          // Reset local imediato para melhorar a experiência do utilizador
          setHistorico([]);
          setSugestao(null);
          alert("Histórico removido com sucesso!");
        }
      } catch (err) {
        console.error("Erro ao resetar dados:", err);
      }
    }
  };

  useEffect(() => {
    fetchDados();
    // Polling de 5 segundos para manter os dados atualizados
    const interval = setInterval(fetchDados, 5000);
    return () => clearInterval(interval);
  }, []);

  const enviarNumero = async (n: number) => {
    try {
      await fetch('http://localhost:8000/input', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ numero: n })
      });
      fetchDados();
    } catch (err) {
      console.error("Erro ao enviar número:", err);
    }
  };

  return (
    <div className="p-8 text-white bg-gray-900 min-h-screen">
      <header className="mb-12">
        <h1 className="text-4xl font-bold mb-2">Análise Preditiva - Roleta</h1>
        <p className="text-gray-400">Insira os resultados para gerar a probabilidade</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Lado Esquerdo: Input de dados */}
        <section className="bg-gray-800 p-6 rounded-xl border border-gray-700">
          <h2 className="text-xl mb-4 font-semibold">Entrada de Giros</h2>
          <div className="grid grid-cols-6 gap-2">
            {[...Array(37).keys()].map((n) => (
              <button
                key={n}
                onClick={() => enviarNumero(n)}
                className={`p-3 rounded font-bold hover:scale-105 transition-all ${
                  n === 0 ? 'bg-green-600' : 
                  [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36].includes(n) ? 'bg-red-600' : 'bg-black'
                }`}
              >
                {n}
              </button>
            ))}
          </div>
        </section>

        {/* Lado Direito: Dashboard de Resultados */}
        <section className="space-y-6">
          {/* Sugestão de Jogada */}
          <div className="bg-blue-900/20 p-6 rounded-xl border border-blue-500/30">
            <h2 className="text-blue-400 text-xs uppercase tracking-widest mb-3 font-bold">Próxima Jogada Sugerida</h2>
            {sugestao && !sugestao.mensagem ? (
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-4xl font-black uppercase tracking-tight">{sugestao.sugestao}</p>
                  <p className="text-gray-400 text-xs mt-1">
                    Balanceamento: Vermelho ({sugestao.analise.V}) | Preto ({sugestao.analise.P})
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-gray-500 italic text-sm">
                {sugestao?.mensagem || "Aguardando volume de dados para análise..."}
              </p>
            )}
          </div>

          {/* Histórico com Botão de Reset Integrado */}
          <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-sm text-gray-400 uppercase tracking-wider font-bold">Histórico Recente (Redis)</h2>
              
              {/* Botão de Limpeza com estilo de aviso (Red) */}
              <button 
                onClick={resetarDados}
                className="text-[10px] uppercase font-bold bg-red-600/10 hover:bg-red-600 text-red-500 hover:text-white py-1.5 px-3 rounded-lg border border-red-600/20 transition-all"
              >
                Limpar Banco
              </button>
            </div>

            <div className="flex gap-3 overflow-x-auto pb-4 custom-scrollbar">
              {historico && historico.length > 0 ? (
                historico.map((giro, i) => (
                  <div 
                    key={i} 
                    className={`min-w-[42px] h-10 flex items-center justify-center rounded-lg font-bold border-2 transition-transform hover:scale-110 ${
                      giro.cor === 'vermelho' ? 'border-red-600/50 bg-red-600/10 text-red-500' : 
                      giro.cor === 'preto' ? 'border-gray-500/50 bg-black text-white' : 'border-green-600/50 bg-green-600/10 text-green-500'
                    }`}
                  >
                    {giro.numero}
                  </div>
                ))
              ) : (
                <div className="w-full py-4 text-center border border-dashed border-gray-700 rounded-lg">
                  <p className="text-gray-600 text-xs italic">Nenhum dado encontrado na cache.</p>
                </div>
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default App;