import { ChatClient } from "@/components/chat-client";

export default function ChatPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
          Chat Bot
        </h1>
        <p className="text-sm text-zinc-500">
          Interface pronta; a busca semântica sobre os documentos coletados
          (RAG via Voyage AI) ainda não está configurada.
        </p>
      </div>
      <ChatClient />
    </div>
  );
}
