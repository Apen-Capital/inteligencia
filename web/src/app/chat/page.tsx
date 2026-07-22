import { ChatClient } from "@/components/chat-client";

export default function ChatPage() {
  return (
    <div className="flex h-[calc(100vh-14rem)] flex-col space-y-6">
      <div className="space-y-2">
        <p className="font-mono text-xs uppercase tracking-widest text-muted-foreground">
          Chat
        </p>
        <h1 className="font-display text-3xl text-foreground">
          Consulte a inteligência coletada
        </h1>
        <p className="max-w-2xl text-sm text-muted-foreground">
          Busca semântica real via Voyage AI sobre os documentos coletados.
          Geração de resposta em linguagem natural (Claude) ainda não
          configurada — você vê os trechos mais relevantes encontrados.
        </p>
      </div>
      <ChatClient />
    </div>
  );
}
