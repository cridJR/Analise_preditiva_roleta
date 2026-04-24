import { useState, useEffect } from 'react';

interface RegistroGiro {
  numero: number;
  cor: string;
  paridade: string;
  duzia: number;
  coluna: number;
  metade: string;
  setor: string; // Novo campo vindo do backend
}

function App() {
  const [historico, setHistorico] = useState<RegistroGiro[]>([]);
  const [analise, setAnalise] = useState<any>(null);

  const fetchDados = async () => {
    try {
      const h = await fetch('http://localhost:8000/historico').then(r => r.json());
      const s = await fetch('http://localhost:8000/sugestao').then(r => r.json());
      setHistorico(h);
      setAnalise(s);
    } catch (e) { console.error("Erro na conexão com a API"); }
  };

  const enviar = async (n: number) => {
    await fetch('http://localhost:8000/input', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ numero: n })
    });
    fetchDados();
  };

  const resetarBanco = async () => {
    if (window.confirm("Zerar todo o histórico do cilindro no Redis?")) {
      await fetch('http://localhost:8000/limpar-historico', { method: 'DELETE' });
      fetchDados();
    }
  };

  useEffect(() => {
    fetchDados();
    const interval = setInterval(fetchDados, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6 bg-slate-950 min-h-screen text-slate-200 font-sans">
      <div className="max-w-6xl mx-auto">
        
        {/* HEADER */}
        <header className="flex justify-between items-center mb-10 border-b border-slate-800 pb-8">
          <div>
            <h1 className="text-3xl font-black text-emerald-400 tracking-tighter italic">ROULETTE ANALYZER PRO</h1>
            <div className="flex gap-3 mt-4">
              <div className="bg-red-600/20 border border-red-500/30 px-3 py-1 rounded text-red-500 text-[10px] font-black uppercase">
                {analise?.v || 0} Vermelhos
              </div>
              <div className="bg-slate-800 border border-slate-700 px-3 py-1 rounded text-slate-400 text-[10px] font-black uppercase">
                {analise?.p || 0} Pretos
              </div>
            </div>
          </div>

          <button 
            onClick={resetarBanco}
            className="bg-red-600 hover:bg-red-500 text-white font-black py-2 px-6 rounded shadow-lg shadow-red-900/40 transition-all text-xs"
          >
            LIMPAR REDIS
          </button>
        </header>

        <div className="grid lg:grid-cols-3 gap-8">
          
          {/* MESA DE ENTRADA */}
          <div className="lg:col-span-2 bg-slate-900 p-8 rounded-3xl border border-slate-800 shadow-2xl">
            <h2 className="text-slate-500 text-[10px] font-black uppercase mb-6 tracking-[0.2em]">Selecione o Resultado</h2>
            <div className="grid grid-cols-6 sm:grid-cols-9 gap-3">
              {[...Array(37).keys()].map(n => (
                <button 
                  key={n} 
                  onClick={() => enviar(n)} 
                  className={`h-12 rounded-xl font-black transition-all active:scale-90 hover:scale-105 ${
                    n === 0 ? 'bg-emerald-600 shadow-emerald-900/20' : 
                    [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36].includes(n) ? 'bg-red-600 shadow-red-900/20' : 'bg-black border border-slate-700'
                  } shadow-md`}
                >
                  {n}
                </button>
              ))}
            </div>
          </div>

          {/* PAINEL DE ANÁLISE */}
          <div className="space-y-6">
            <div className="bg-emerald-500/5 p-6 rounded-3xl border border-emerald-500/20">
              <h2 className="text-emerald-500 text-[10px] font-black uppercase mb-4 tracking-widest text-center">IA Suggestions</h2>
              <div className="space-y-3">
                {analise?.sugestoes ? analise.sugestoes.map((s:string, i:number) => (
                  <div 
                    key={i} 
                    className={`font-black p-4 rounded-xl text-center uppercase tracking-tight shadow-lg animate-pulse ${
                      s.includes("SETOR") 
                      ? 'bg-amber-500 text-amber-950 border-2 border-amber-400' // Destaque para Cilindro
                      : 'bg-emerald-500 text-slate-950' // Destaque para Matemática
                    }`}
                  >
                    {s}
                  </div>
                )) : <p className="text-slate-600 text-center italic text-xs py-4">{analise?.mensagem || "Monitorando mesa..."}</p>}
              </div>
            </div>

            {/* HISTÓRICO COM SETORES */}
            <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800">
              <h2 className="text-[10px] font-black text-slate-600 uppercase mb-4 tracking-widest text-center">Timeline Física</h2>
              <div className="flex gap-3 overflow-x-auto pb-4 scrollbar-hide">
                {historico.map((g, i) => (
                  <div key={i} className="flex flex-col items-center gap-1">
                    <div className={`min-w-[40px] h-10 flex items-center justify-center rounded-lg font-black text-xs ${
                      g.cor === 'vermelho' ? 'bg-red-600' : g.cor === 'preto' ? 'bg-black border border-slate-800' : 'bg-emerald-600'
                    }`}>
                      {g.numero}
                    </div>
                    <span className="text-[8px] font-bold text-slate-500 uppercase">{g.setor.substring(0, 3)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;