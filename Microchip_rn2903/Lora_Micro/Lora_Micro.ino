/* RN2483 LoRa OTAA
 *
 * Comunicazione via LoRa usando il modulo LoRa RN2903 di Microchip
 *
 * Sesnore di temperatura OneWire DS18B20
 *
 * -------------------------------------------------------------------------
 * Arduino esegue il campionamento dal sensore e poi via seriale comunica
 * con il modulo per trasmettere a TTN i dati ottenuti
 * -------------------------------------------------------------------------
 *
 *  Pin di connessione tra la scheda RN2XX3 e Arduino:
 *
 * RN2xx3 <--> Arduino
 * Uart TX <--> 10
 * Uart RX <--> 11
 * MCLR <--> 12
 * Vcc <--> 3.3V
 * Gnd <--> Gnd
 *
*/

#include <rn2xx3.h>             //Libreria per modulo LoRa
#include <SoftwareSerial.h>     //Libreria per la comunicazione seriale su una porta non RX,TX
#include <OneWire.h>            //Libreria per la comunicazione OneWire del sensore
#include <DallasTemperature.h>  //Libreria per l'elaborazione della temperatura

#define ONE_WIRE_BUS 2 //Pin su cui è connseeso il sensore DS18B20

OneWire oneWire(ONE_WIRE_BUS);  //Creo un istanza per comunicare col mio sensore OneWire
DallasTemperature sensors(&oneWire); //passo l'istanza su cui verranno eseguite le elaborazioni

SoftwareSerial mySerial(10, 11); // RX, TX


rn2xx3 myLora(mySerial); //creazione di un istanza della libreria rn2xx3 con passagio della seriale su cui mandare i messaggi


void setup()
{

  pinMode(13, OUTPUT);
  led_on();

  //Dichiarazione delle porte seriali

  Serial.begin(57600); //Porta seriale per la comunicazione con PC
  mySerial.begin(9600); //Porta seriale per la comunicazione con RN2483
  Serial.println("Startup");

  initialize_radio(); //inizializzo il modulo
  sensors.begin(); //inizializzo il sensore

  //Trasmissione di un messaggio di Setup
  myLora.tx("TTN Mapper sul nodo TTN ");

  led_off();
  delay(2000); //aspetto 2 secondi prima di iniziare con la trasmissione
}

void initialize_radio()
{
  //Resetto la scheda RN2483
  pinMode(12, OUTPUT);
  digitalWrite(12, LOW);
  delay(500);
  digitalWrite(12, HIGH);

  delay(100); //Aspetto il messaggio di startup da RN2483
  mySerial.flush();

  //Autobaud del modulo RN2483 a 9600.Default a 57600.
  myLora.autobaud();

  //Provo a vedere se il modulo mi risponde
  String hweui = myLora.hweui();
  while(hweui.length() != 16)
  {
    Serial.println("Errore di connessione con la board RN2xx3");
    Serial.println(hweui);
    delay(10000);
    hweui = myLora.hweui();
  }

  //Stampo il HWEUI con cui ci registriamo via ttnctl
  Serial.println("Quando usi OTAA, registra questo DevEUI: ");
  Serial.println(myLora.hweui());
  Serial.println("versione firmware RN2xx3:");
  Serial.println(myLora.sysver());

  //Parte di configurazione delle chiavi per la connessione
  Serial.println("Connettendomi a TTN...");
  bool join_result = false;

  /*
   * OTAA: initOTAA(String AppEUI, String AppKey);
   * Copiare i codici dati dalla console TTN in fondo alla pagina qui:*/
  const char *appEui = "70B3D57ED000xxxx";
  const char *appKey = "C94BA7258716D9402CC3C8BFE27xxxxx";

  Serial.println("appEui: "+(String)appEui);
  Serial.println("appKey: "+(String)appKey);

  join_result = myLora.initOTAA(appEui, appKey); //apre la connsessione con i nostri paramtri


  while(!join_result) //Attende la connessione
  {
    Serial.println("Problemi di connessione a TTN,potrebbe non esserci segnale o i dati inseriti potrebbero non essere corretti");
    delay(2500); //Aspetta 2.5 secondi prima di tentare una nuova connessione
    join_result = myLora.init();
  }
  Serial.println("Connesso a TTN correttamente");

}

void loop()
{
    led_on();
    Serial.print(" Recupero la temperatura...");
    sensors.requestTemperatures(); //leggo la temperatura

    float temperatura = sensors.getTempCByIndex(0); //mi salvo in una variabile la teperatura rilevata
    Serial.print("Temperatura: "+(String)temperatura);

    Serial.println("--Trasmettendo-->");
    myLora.tx(String(temperatura));

    led_off();
    delay(180000);//mando ogni 3 minuti
}

void led_on()
{
  digitalWrite(13, 1);
}

void led_off()
{
  digitalWrite(13, 0);
}
