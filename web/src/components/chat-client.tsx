"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

type Resultado = {
  fonte: string;
  grupo: string;
  titulo: string | null;
  trecho: string;
  url: string;
  similaridade: number;
};

type Mensagem = {
  papel: "usuario" | "assistente";
  texto: string;
  resultados?: Resultado[];
};

export function ChatClient() {
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [entrada, setEntrada] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function enviar() {
    const texto = entrada.trim();
    if (!texto || enviando) return;

    setMensagens((atuais) => [...atuais, { papel: "usuario", texto }]);
    setEntrada("");
    setEnviando(true);

    try {
      const resposta = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensagem: texto }),
      });
      const dados = await resposta.json();
      const textoResposta = resposta.ok
        ? dados.resposta
        : (dados.erro ?? "Erro ao processar a mensagem.");
      setMensagens((atuais) => [
        ...atuais,
        {
          papel: "assistente",
          texto: textoResposta,
          resultados: resposta.ok ? dados.resultados : undefined,
        },
      ]);
    } catch {
      setMensagens((atuais) => [
        ...atuais,
        {
          papel: "assistente",
          texto: "Erro ao falar com o servidor. Tente novamente.",
        },
      ]);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="flex flex-1 flex-col overflow-hidden border border-border">
      <div className="flex-1 space-y-6 overflow-y-auto p-6">
        {mensagens.length === 0 && (
          <p className="font-mono text-xs text-muted-foreground">
            &gt; faça uma pergunta sobre os documentos coletados
          </p>
        )}
        {mensagens.map((m, i) => (
          <div key={i} className="space-y-3">
            {m.papel === "usuario" ? (
              <p className="font-mono text-sm text-primary">
                <span className="text-muted-foreground">&gt; </span>
                {m.texto}
              </p>
            ) : (
              <>
                <p className="max-w-2xl text-sm leading-relaxed text-foreground">
                  {m.texto}
                </p>
                {m.resultados && m.resultados.length > 0 && (
                  <div className="space-y-2 border-l-2 border-primary/30 pl-4">
                    {m.resultados.map((r, j) => (
                      <div key={j} className="space-y-1">
                        <div className="flex items-center gap-2 font-mono text-[11px] text-muted-foreground">
                          <span className="text-primary">{r.fonte}</span>
                          <span>· {r.grupo}</span>
                          <span>· similaridade {r.similaridade}</span>
                        </div>
                        {r.titulo && (
                          <p className="font-display text-sm text-foreground">
                            {r.titulo}
                          </p>
                        )}
                        <p className="text-xs leading-relaxed text-muted-foreground">
                          {r.trecho}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        ))}
        {enviando && (
          <p className="font-mono text-xs text-muted-foreground">
            buscando...
          </p>
        )}
      </div>
      <div className="flex gap-2 border-t border-border p-4">
        <Textarea
          value={entrada}
          onChange={(e) => setEntrada(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              enviar();
            }
          }}
          placeholder="Pergunte algo sobre os documentos coletados..."
          className="min-h-0 resize-none border-border font-mono text-sm"
          rows={2}
        />
        <Button
          onClick={enviar}
          disabled={enviando}
          className="bg-primary text-primary-foreground hover:bg-primary/90"
        >
          Enviar
        </Button>
      </div>
    </div>
  );
}
