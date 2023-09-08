#include <stdio.h>  // Standard I/O functions
#include <stdlib.h> // Standard library functions

#include <time.h>
#include <string.h>
#include "contiki.h"
#include "coap-engine.h"
#include "sys/etimer.h"
#include "coap-blocking-api.h"
#include "random.h"
#include "os/dev/serial-line.h"
#include "dev/button-hal.h"



// Parameter definitions
#define GLOBAL_VERBOSE 1 // enable or disable printf debugs
#define RESOURCE_NAME "food"
#define MESSAGE_TEMPLATE "food_%d"
#define STATE_BOOT 0
#define STATE_INIT 1
#define STATE_CONNECTING 2
#define STATE_CONNECTED 3
#define STATE_DISCONNECTED 4
#define SERVER_EP "coap://[fd00::1]:5683"
#define SERVICE_URL "hello"

// global variables
char message_buffer[32]; // global buffer for messages
int event_notify;
int time_counter;
int status;
int my_id;

// Custom function prototypes
int produce_self_id(void);
void log_message(const char *message);

// contiki variable declarations
static struct etimer et;
extern coap_resource_t res_status;
static coap_endpoint_t serverCoap;
static coap_message_t request[1];


// contiki function prototypes

static void res_event_handler(void){
    coap_notify_observers(&res_status);
}


static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset){
    coap_set_header_content_format(response, APPLICATION_JSON);
    sprintf((char *)buffer, "{\"status\": %d}", status);
    coap_set_payload(response, buffer, strlen((char*)buffer));
}

static void res_post_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset){
    size_t len = 0;
    const char *command = NULL;
    int success  = 0;
    if((len = coap_get_post_variable(request, "command", &command))) {
        // status == 0 (food refiller close)
        if (strncmp(command, "0", len) == 0){
            coap_set_status_code(response,VALID_2_03);
            status = 0;
            success = 1;
        }
            // status == 1 (food refiller open)
        else if (strncmp(command, "1", len) == 0){
            coap_set_status_code(response,VALID_2_03);
            status = 1;
            success = 1;
        }
    }

    if (!success){
        coap_set_status_code(response, BAD_REQUEST_4_00);
    }
}
// This function is will be passed to COAP_BLOCKING_REQUEST() to handle responses.
void client_chunk_handler(coap_message_t *response) {
    const uint8_t *chunk;

    if (response == NULL) {
        printf("risposta null \n");
        return;
    }
    char buff[50];
    sprintf(buff, "%d", coap_get_payload(response, &chunk));
    log_message(buff);
}

// Contiki resource
EVENT_RESOURCE(res_status, "title=\"Status \" POST command=0|1|2;food;rt=\"status\"", res_get_handler,  res_post_handler, NULL, NULL, res_event_handler);

int main() {
    my_id = 0;
    event_notify = 0;
    time_counter = -1;
    status = STATE_BOOT;

    coap_activate_resource(&res_status, "food");
    coap_endpoint_parse(SERVER_EP, strlen(SERVER_EP), &serverCoap);
    coap_init_message(request, COAP_TYPE_CON, COAP_GET, 0);
    coap_set_header_uri_path(request, SERVICE_URL);

    while(1){

        if(time_counter<0){
            time_counter = 0;
            status = STATE_INIT;
            etimer_set(&et, CLOCK_SECOND);
         }
        if(etimer_expired(&et)) {
            time_counter ++;
            etimer_set(&et, CLOCK_SECOND);
        }
        if((time_counter > 2) || (event_notify>0)){
            // time_counter: periodic operations, based on internal state
            // event_notify: asynchronous events
            if(status == STATE_INIT){
                log_message("COAP NODE: state init");
                status = STATE_CONNECTING;
                my_id = produce_self_id();

                printf("COAP node awaken: %d",my_id);
            }
            if((status == STATE_CONNECTING)||(status==STATE_CONNECTED)){
                snprintf(message_buffer, sizeof(message_buffer),MESSAGE_TEMPLATE, my_id);
                log_message("COAP NODE: sending request");

                coap_set_payload(request, (uint8_t *) message_buffer, sizeof(message_buffer) - 1);
                COAP_BLOCKING_REQUEST(&serverCoap, request, client_chunk_handler);
            }

            // cleanup
            if(status == STATE_DISCONNECTED){
                // reset if error occurred
                time_counter = -1;
                event_notify = 0;
                status = STATE_BOOT;
            }
            else {
                time_counter = 0;
                event_notify = 0;
            }
        }
    }
}

// Use printf to display the message to the console in the preferred way
void log_message(const char *message) {
    if (GLOBAL_VERBOSE){
        printf("%s", message);
    }

}
int produce_self_id() {
    return 501 + (int) rand();
}