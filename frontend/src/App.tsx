import { useState, useEffect } from 'react';

function App() {
  const [historico, setHistorico] = useState<any[]>([]);
  const [analise, setAnalise] = useState<any>(null);

  const fetchDados = async () => {
    try {
      const resH = await fetch('http://localhost:8000/historico');
      const dataH = await resH.json();
      setHistorico(dataH);

      const resS = await fetch('http://localhost:8000/sugestao');
      const dataS = await resS.json();
      setAnalise(dataS);
    } catch (e) { console.error("API Offline"); }
  };

  const enviarNumero = async (n: number) => {
    await fetch('http://localhost:8000/input', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ numero: n })
    });
    fetchDados();
  };

  useEffect(() => {
    fetchDados();
    const t = setInterval(fetchDados, 5000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="p-6 bg-slate-900 min-h-screen text-white font-sans">
      <div className="max-w-6xl mx-auto">
        <header className="flex justify-between items-center mb-8 border-b border-slate-800 pb-4">
          <h1 className="text-2xl font-black">ROULETTE <span className="text-emerald-500">PRO ANALYZER</span></h1>
          <div className="flex gap-4">
             <div className="flex items-center gap-2 bg-slate-800 px-3 py-1 rounded-full border border-red-500/30">
                <div className="w-3 h-3 bg-red-600 rounded-full animate-pulse"></div>
                <span className="text-xs font-bold">{analise?.v || 0} Vermelhos</span>
             </div>
             <div className="flex items-center gap-2 bg-slate-800 px-3 py-1 rounded-full border border-gray-500/30">
                <div className="w-3 h-3 bg-black rounded-full border border-white/20"></div>
                <span className="text-xs font-bold">{analise?.p || 0} Pretos</span>
             </div>
          </div>
        </header>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* MESA DE INPUT */}
          <div className="lg:col-span-2 bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-2xl">
            <h2 className="text-sm font-black text-slate-500 uppercase mb-4 tracking-widest">Entrada de Giros</h2>
            <div className="grid grid-cols-6 sm:grid-cols-9 gap-2">
              {[...Array(37).keys()].map(n => (
                <button key={n} onClick={() => enviarNumero(n)} className={`h-12 rounded-lg font-bold transition-all active:scale-90 hover:brightness-125 ${n === 0 ? 'bg-emerald-600' : [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36].includes(n) ? 'bg-red-600' : 'bg-slate-950'}`}>
                  {n}
                </button>
              ))}
            </div>
          </div>

          {/* PAINEL DE SUGESTÕES */}
          <div className="space-y-4">
            <div className="bg-emerald-500/10 p-6 rounded-2xl border border-emerald-500/30">
              <h2 className="text-emerald-500 text-xs font-black uppercase mb-4 tracking-tighter">Sugestões de Entrada</h2>
              {analise?.sugestoes ? (
                <div className="space-y-2">
                  {analise.sugestoes.map((s: string, i: number) => (
                    <div key={i} className="bg-emerald-500 text-slate-900 font-black p-3 rounded-lg text-center uppercase animate-in slide-in-from-right duration-300">
                      {s}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-slate-500 italic text-sm text-center py-4">{analise?.mensagem || "Aguardando dados..."}</p>
              )}
            </div>

            {/* HISTÓRICO */}
            <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700">
              <h2 className="text-xs font-bold text-slate-500 uppercase mb-4">Últimos 100 Giros</h2>
              <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
                {historico.map((g, i) => (
                  <div key={i} className={`min-w-[35px] h-9 flex items-center justify-center rounded font-bold text-xs ${g.cor === 'vermelho' ? 'bg-red-600' : g.cor === 'preto' ? 'bg-slate-950' : 'bg-emerald-600'}`}>
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