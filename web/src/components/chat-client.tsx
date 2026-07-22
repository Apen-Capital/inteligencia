"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";

type Mensagem = {
  papel: "usuario" | "assistente";
  texto: string;
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
        { papel: "assistente", texto: textoResposta },
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
    <Card className="flex h-[70vh] flex-col">
      <ScrollArea className="flex-1 p-4">
        {mensagens.length === 0 && (
          <p className="text-sm text-zinc-500">
            Faça uma pergunta sobre os documentos coletados. (Integração real
            com busca semântica ainda não configurada — ver README.md.)
          </p>
        )}
        <div className="space-y-3">
          {mensagens.map((m, i) => (
            <div
              key={i}
              className={
                m.papel === "usuario"
                  ? "ml-auto max-w-[80%] rounded-lg bg-zinc-900 px-3 py-2 text-sm text-zinc-50 dark:bg-zinc-50 dark:text-zinc-900"
                  : "mr-auto max-w-[80%] rounded-lg bg-zinc-100 px-3 py-2 text-sm text-zinc-900 dark:bg-zinc-800 dark:text-zinc-50"
              }
            >
              {m.texto}
            </div>
          ))}
        </div>
      </ScrollArea>
      <CardContent className="flex gap-2 border-t p-4">
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
          className="min-h-0 resize-none"
          rows={2}
        />
        <Button onClick={enviar} disabled={enviando}>
          Enviar
        </Button>
      </CardContent>
    </Card>
  );
}
