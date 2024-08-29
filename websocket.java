import javax.websocket.*;
import java.net.URI;
import java.util.concurrent.TimeUnit;

@ClientEndpoint
public class WebSocketClient {

    private Session session;
    private final String uri = "ws://localhost:8080"; // Altere para o endereço do seu servidor WebSocket

    public WebSocketClient() {
        connect();
    }

    @OnOpen
    public void onOpen(Session session) {
        this.session = session;
        System.out.println("Conexão WebSocket estabelecida");
        sendMessage("Olá, servidor!");
    }

    @OnMessage
    public void onMessage(String message) {
        System.out.println("Mensagem do servidor: " + message);
    }

    @OnClose
    public void onClose(Session session, CloseReason closeReason) {
        System.out.println("Conexão WebSocket fechada. Motivo: " + closeReason);
        reconnect();
    }

    @OnError
    public void onError(Session session, Throwable throwable) {
        System.err.println("Erro no WebSocket: " + throwable.getMessage());
        reconnect();
    }

    private void connect() {
        try {
            WebSocketContainer container = ContainerProvider.getWebSocketContainer();
            container.connectToServer(this, URI.create(uri));
        } catch (Exception e) {
            e.printStackTrace();
            reconnect();
        }
    }

    private void reconnect() {
        try {
            TimeUnit.SECONDS.sleep(5); // Espera 5 segundos antes de tentar reconectar
            System.out.println("Tentando reconectar...");
            connect();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    public void sendMessage(String message) {
        try {
            session.getAsyncRemote().sendText(message);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        new WebSocketClient();
    }
}

