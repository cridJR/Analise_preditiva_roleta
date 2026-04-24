import { useState, useEffect } from 'react';

interface RegistroGiro {
  numero: number;
  cor: string;
  paridade: string;
  duzia: number;
  coluna: number;
  metade: string;
}

interface Sugestao {
  analise: { V: number; P: number; };
  sugestao: string;
  mensagem?: string; 
}

function App() {
  const [historico, setHistorico] = useState<RegistroGiro[]>([]);
  const [sugestao, setSugestao] = useState<Sugestao | null>(null);

  const fetchDados = async () => {
    try {
      const resHist = await fetch('http://localhost:8000/historico');
      const dataHist = await resHist.json();
      setHistorico(Array.isArray(dataHist) ? dataHist : []);

      const resSug = await fetch('http://localhost:8000/sugestao');
      const dataSug = await resSug.json();
      setSugestao(dataSug);
    } catch (err) {
      console.error("Erro ao conectar com API:", err);
    }
  };

  const resetarDados = async () => {
    if (window.confirm("Deseja realmente resetar todos os dados do Redis?")) {
      try {
        await fetch('http://localhost:8000/limpar-historico', { method: 'DELETE' });
        setHistorico([]);
        setSugestao(null);
      } catch (err) {
        alert("Erro ao limpar dados");
      }
    }
  };

  const enviarNumero = async (n: number) => {
    try {
      await fetch('http://localhost:8000/input', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ numero: n })
      });
      fetchDados();
    } catch (err) {
      console.error("Erro ao enviar:", err);
    }
  };

  useEffect(() => {
    fetchDados();
    const interval = setInterval(fetchDados, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-8 text-white bg-gray-900 min-h-screen font-sans">
      <header className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-black text-white tracking-tight">ANALYSIS PRO</h1>
          <p className="text-gray-400 text-sm">Monitoramento de Desvio Estatístico</p>
        </div>
        <button 
          onClick={resetarDados}
          className="bg-red-600 hover:bg-red-700 text-white text-xs font-bold py-2 px-4 rounded transition-all"
        >
          RESETAR REDIS
        </button>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Painel de Entrada */}
        <section className="bg-gray-800 p-6 rounded-2xl border border-gray-700 shadow-xl">
          <h2 className="text-lg font-bold mb-4 text-gray-200">Mesa de Entrada</h2>
          <div className="grid grid-cols-6 gap-2">
            {[...Array(37).keys()].map((n) => (
              <button
                key={n}
                onClick={() => enviarNumero(n)}
                className={`p-3 rounded-lg font-bold transition-transform active:scale-95 ${
                  n === 0 ? 'bg-green-600' : 
                  [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36].includes(n) ? 'bg-red-600' : 'bg-black'
                }`}
              >
                {n}
              </button>
            ))}
          </div>
        </section>

        {/* Dashboard de Análise */}
        <section className="space-y-4">
          {/* Cards de Métricas Rápidas */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-800 p-4 rounded-xl border border-gray-700">
              <span className="text-[10px] text-gray-500 font-bold uppercase">Últimas Dúzias</span>
              <div className="flex gap-2 mt-1">
                {historico.slice(0, 5).map((g, i) => (
                  <span key={i} className="text-xs font-mono bg-gray-900 px-2 py-1 rounded border border-gray-700">
                    {g.duzia}ª
                  </span>
                ))}
              </div>
            </div>
            <div className="bg-gray-800 p-4 rounded-xl border border-gray-700">
              <span className="text-[10px] text-gray-500 font-bold uppercase">Últimas Colunas</span>
              <div className="flex gap-2 mt-1">
                {historico.slice(0, 5).map((g, i) => (
                  <span key={i} className="text-xs font-mono bg-gray-900 px-2 py-1 rounded border border-gray-700">
                    {g.coluna}ª
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Sugestão de Entrada */}
          <div className="bg-indigo-600/20 p-6 rounded-2xl border border-indigo-500/40">
            <h2 className="text-indigo-400 text-xs font-black uppercase tracking-tighter mb-1">Sugestão do Algoritmo</h2>
            {sugestao && !sugestao.mensagem ? (
              <div>
                <p className="text-5xl font-black text-white">{sugestao.sugestao}</p>
                <div className="mt-2 flex gap-4 text-[10px] font-bold text-gray-400">
                  <span>VERMELHOS: {sugestao.analise.V}</span>
                  <span>PRETOS: {sugestao.analise.P}</span>
                </div>
              </div>
            ) : (
              <p className="text-gray-500 italic text-sm py-4">{sugestao?.mensagem || "Aguardando entrada..."}</p>
            )}
          </div>

          {/* Histórico Visual */}
          <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700">
            <h2 className="text-xs font-bold text-gray-500 uppercase mb-4 tracking-widest">Fluxo Recente</h2>
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
              {historico.length > 0 ? (
                historico.map((g, i) => (
                  <div 
                    key={i} 
                    className={`min-w-[45px] h-11 flex items-center justify-center rounded-lg font-black text-lg border-b-4 ${
                      g.cor === 'vermelho' ? 'bg-red-600 border-red-800 text-white' : 
                      g.cor === 'preto' ? 'bg-zinc-900 border-black text-white' : 'bg-green-600 border-green-800 text-white'
                    }`}
                  >
                    {g.numero}
                  </div>
                ))
              ) : (
                <p className="text-gray-600 text-xs italic">Nenhum dado na cache do Redis.</p>
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default App;