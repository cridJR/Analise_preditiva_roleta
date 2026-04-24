import { useState, useEffect } from 'react';

function App() {
  const [historico, setHistorico] = useState<any[]>([]);
  const [analise, setAnalise] = useState<any>(null);

  const fetchDados = async () => {
    try {
      const h = await fetch('http://localhost:8000/historico').then(r => r.json());
      const s = await fetch('http://localhost:8000/sugestao').then(r => r.json());
      setHistorico(h);
      setAnalise(s);
    } catch (e) { console.error("API Error"); }
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
    if (window.confirm("Zerar todos os dados do Redis?")) {
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
    <div className="p-6 bg-slate-950 min-h-screen text-slate-200">
      <div className="max-w-6xl mx-auto">
        
        {/* HEADER COM CONTADORES E RESET */}
        <header className="flex justify-between items-center mb-10 border-b border-slate-800 pb-8">
          <div>
            <h1 className="text-3xl font-black text-emerald-400 tracking-tighter">ANALYZER PRO</h1>
            <div className="flex gap-3 mt-4">
              <div className="bg-red-600/20 border border-red-500/30 px-3 py-1 rounded text-red-500 text-xs font-black uppercase">
                {analise?.v || 0} Vermelhos
              </div>
              <div className="bg-slate-800 border border-slate-700 px-3 py-1 rounded text-slate-400 text-xs font-black uppercase">
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
          {/* MESA DE NÚMEROS */}
          <div className="lg:col-span-2 bg-slate-900 p-8 rounded-3xl border border-slate-800 shadow-inner">
            <div className="grid grid-cols-6 sm:grid-cols-9 gap-3">
              {[...Array(37).keys()].map(n => (
                <button key={n} onClick={() => enviar(n)} className={`h-12 rounded-lg font-black transition-all active:scale-90 hover:brightness-125 ${n === 0 ? 'bg-emerald-600' : [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36].includes(n) ? 'bg-red-600' : 'bg-black border border-slate-700'}`}>
                  {n}
                </button>
              ))}
            </div>
          </div>

          {/* PAINEL DE SUGESTÕES */}
          <div className="space-y-6">
            <div className="bg-emerald-500/5 p-6 rounded-3xl border border-emerald-500/20">
              <h2 className="text-emerald-500 text-[10px] font-black uppercase mb-4 tracking-widest text-center">Sugestões de Entrada</h2>
              <div className="space-y-3">
                {analise?.sugestoes ? analise.sugestoes.map((s:any, i:any) => (
                  <div key={i} className="bg-emerald-500 text-slate-950 font-black p-4 rounded-xl text-center uppercase tracking-tight">
                    {s}
                  </div>
                )) : <p className="text-slate-600 text-center italic text-xs py-4">{analise?.mensagem || "Aguardando dados..."}</p>}
              </div>
            </div>

            <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800">
              <h2 className="text-[10px] font-black text-slate-600 uppercase mb-4 tracking-widest text-center">Histórico</h2>
              <div className="flex gap-2 overflow-x-auto pb-4 scrollbar-hide">
                {historico.map((g, i) => (
                  <div key={i} className={`min-w-[36px] h-9 flex items-center justify-center rounded-md font-bold text-[10px] ${g.cor === 'vermelho' ? 'bg-red-600' : g.cor === 'preto' ? 'bg-black border border-slate-800' : 'bg-emerald-600'}`}>
                    {g.numero}
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