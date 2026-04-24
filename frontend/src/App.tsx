import { useState, useEffect } from 'react';

interface RegistroGiro {
  numero: number; cor: string; paridade: string; duzia: number; coluna: number; metade: string;
}

function App() {
  const [historico, setHistorico] = useState<RegistroGiro[]>([]);
  const [sugestao, setSugestao] = useState<any>(null);

  const fetchDados = async () => {
    try {
      const resH = await fetch('http://localhost:8000/historico');
      const dataH = await resH.json();
      setHistorico(Array.isArray(dataH) ? dataH : []);

      const resS = await fetch('http://localhost:8000/sugestao');
      const dataS = await resS.json();
      setSugestao(dataS);
    } catch (e) { console.error("API offline"); }
  };

  const enviarNumero = async (n: number) => {
    await fetch('http://localhost:8000/input', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ numero: n })
    });
    fetchDados();
  };

  const resetar = async () => {
    if (window.confirm("Limpar histórico do Redis?")) {
      await fetch('http://localhost:8000/limpar-historico', { method: 'DELETE' });
      setHistorico([]);
      setSugestao(null);
    }
  };

  useEffect(() => {
    fetchDados();
    const timer = setInterval(fetchDados, 5000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="p-6 bg-gray-900 min-h-screen text-white font-sans">
      <div className="max-w-5xl mx-auto">
        <header className="flex justify-between items-center mb-8 border-b border-gray-800 pb-4">
          <h1 className="text-2xl font-black tracking-tighter">ROULETTE ANALYTICS <span className="text-blue-500">PRO</span></h1>
          <button onClick={resetar} className="text-[10px] border border-red-600/50 text-red-500 px-3 py-1 rounded hover:bg-red-600 hover:text-white transition-all font-bold">RESET REDIS</button>
        </header>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Entrada */}
          <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700">
            <h2 className="text-sm font-bold text-gray-400 mb-4 uppercase">Mesa de Giros</h2>
            <div className="grid grid-cols-6 gap-2">
              {[...Array(37).keys()].map(n => (
                <button key={n} onClick={() => enviarNumero(n)} className={`p-3 rounded-lg font-bold transition-transform active:scale-90 ${n === 0 ? 'bg-green-600' : [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36].includes(n) ? 'bg-red-600' : 'bg-black'}`}>
                  {n}
                </button>
              ))}
            </div>
          </div>

          {/* Painel Lateral */}
          <div className="space-y-4">
            <div className="bg-blue-600/10 p-6 rounded-2xl border border-blue-500/30 text-center">
              <span className="text-[10px] font-black text-blue-400 uppercase tracking-widest">Sugestão Atual</span>
              <p className="text-4xl font-black mt-2">{sugestao?.sugestao || "---"}</p>
              {sugestao?.mensagem && <p className="text-xs text-gray-500 mt-2">{sugestao.mensagem}</p>}
            </div>

            <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700">
              <h2 className="text-xs font-bold text-gray-500 uppercase mb-4">Fluxo Recente</h2>
              <div className="flex gap-2 overflow-x-auto pb-2">
                {historico.length > 0 ? historico.map((g, i) => (
                  <div key={i} className={`min-w-[40px] h-10 flex items-center justify-center rounded font-bold border-b-2 ${g.cor === 'vermelho' ? 'bg-red-600' : g.cor === 'preto' ? 'bg-black' : 'bg-green-600'}`}>
                    {g.numero}
                  </div>
                )) : <p className="text-gray-600 text-xs italic">Aguardando dados...</p>}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;