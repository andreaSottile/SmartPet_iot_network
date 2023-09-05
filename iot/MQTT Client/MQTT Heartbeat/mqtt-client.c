/*
 * Copyright (c) 2020, Carlo Vallati, University of Pisa
  * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the copyright holder nor the names of its
 *    contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 */
/*---------------------------------------------------------------------------*/
#include "contiki.h"
#include "net/routing/routing.h"
#include "mqtt.h"
#include "net/ipv6/uip.h"
#include "net/ipv6/uip-icmp6.h"
#include "net/ipv6/sicslowpan.h"
#include "sys/etimer.h"
#include "sys/ctimer.h"
#include "lib/sensors.h"
#include "dev/button-hal.h"
#include "os/sys/log.h"
#include "mqtt-client.h"

#include <time.h>
#include <string.h>
#include <strings.h>

#include "dev/leds.h"
#include "dev/rgb-led/rgb-led.h"
/*---------------------------------------------------------------------------*/
#define LOG_MODULE "mqtt-client-heartbeat"
#ifdef MQTT_CLIENT_CONF_LOG_LEVEL
#define LOG_LEVEL MQTT_CLIENT_CONF_LOG_LEVEL
#else
#define LOG_LEVEL LOG_LEVEL_DBG
#endif

/*---------------------------------------------------------------------------*/
/* MQTT broker address. */
#define MQTT_CLIENT_BROKER_IP_ADDR "fd00::1"

static const char *broker_ip = MQTT_CLIENT_BROKER_IP_ADDR;

// DefauLt config values
#define DEFAULT_BROKER_PORT         1883
#define DEFAULT_PUBLISH_INTERVAL    (5 * CLOCK_SECOND)

/*---------------------------------------------------------------------------*/
/* Led manipulation */
#define RGB_LED_RED     1
#define RGB_LED_GREEN   2
#define RGB_LED_BLUE    4
#define RGB_LED_MAGENTA (RGB_LED_RED | RGB_LED_BLUE)
#define RGB_LED_YELLOW  (RGB_LED_RED | RGB_LED_GREEN)
#define RGB_LED_CYAN    (RGB_LED_GREEN | RGB_LED_BLUE )
#define RGB_LED_WHITE   (RGB_LED_RED | RGB_LED_GREEN | RGB_LED_BLUE)

void rgb_led_off(void) {
    leds_off(LEDS_ALL);
}

void rgb_led_set(uint8_t colour) {
    leds_mask_t leds =
            ((colour & RGB_LED_RED) ? LEDS_RED : LEDS_COLOUR_NONE) |
            ((colour & RGB_LED_GREEN) ? LEDS_GREEN : LEDS_COLOUR_NONE) |
            ((colour & RGB_LED_BLUE) ? LEDS_BLUE : LEDS_COLOUR_NONE);

    leds_off(LEDS_ALL);
    leds_on(leds);
}

// We assume that the broker does not require authentication


/*---------------------------------------------------------------------------*/
/* Various states */
static uint8_t state;

#define STATE_INIT            0
#define STATE_NET_OK          1
#define STATE_CONNECTING      2
#define STATE_CONNECTED       3
#define STATE_SUBSCRIBED      4
#define STATE_DISCONNECTED    5
#define STATE_PRESUBSCRIBED   6


static uint8_t boot;
#define BOOT_NOT_STARTED      0
#define BOOT_INIT             1
#define BOOT_ID_NEGOTIATION   2
#define BOOT_ID_DENIED        3
#define BOOT_COMPLETED        4
#define BOOT_FAILED           5
/*---------------------------------------------------------------------------*/
/* PUBLISH/SUBSCRIBE MESSAGE TEMPLATES */
#define NODE_TYPE "heartbeat"
#define TOPIC_ID_CONFIG "id_config"
#define TOPIC_SENSOR_DATA "heart_sensor"
#define PUBLISH_MSG_TEMPLATE "pet:%d;freq:%d"
/*---------------------------------------------------------------------------*/
PROCESS_NAME(mqtt_client_process);
AUTOSTART_PROCESSES(&mqtt_client_process);

/*---------------------------------------------------------------------------*/
/* Maximum TCP segment size for outgoing segments of our socket */
#define MAX_TCP_SEGMENT_SIZE    32
#define CONFIG_IP_ADDR_STR_LEN   64
/*---------------------------------------------------------------------------*/
/*
 * Buffers for Client ID and Topics.
 * Make sure they are large enough to hold the entire respective string
 */
#define BUFFER_SIZE 64

static char client_id[BUFFER_SIZE];
static char pub_topic[BUFFER_SIZE];
static char sub_topic[BUFFER_SIZE];

// Periodic timer to check the state of the MQTT client
#define STATE_MACHINE_PERIODIC     (CLOCK_SECOND >> 1)
static struct etimer periodic_timer;
static struct etimer sub_timer; //subscribe simulation timer

/*---------------------------------------------------------------------------*/
/*
 * The main MQTT buffers.
 * We will need to increase if we start publishing more data.
 */
#define APP_BUFFER_SIZE 512
static char app_buffer[APP_BUFFER_SIZE];
/*---------------------------------------------------------------------------*/
static struct mqtt_message *msg_ptr = 0;

static struct mqtt_connection conn;

mqtt_status_t status_HeartTopic;
mqtt_status_t statusId_config;
mqtt_status_t status_Publish;
char broker_address[CONFIG_IP_ADDR_STR_LEN];

/*---------------------------------------------------------------------------*/
PROCESS(mqtt_client_process,
"MQTT Client heartbeat sensor");

static int heartbeat;
unsigned short candidateID = 0;
unsigned short tagId = 0;
static int counter = 0;

/*---------------------------------------------------------------------------*/
static void pub_handler(const char *topic, uint16_t topic_len, const uint8_t *chunk, uint16_t chunk_len) {
    printf("Pub Handler: topic='%s' (len=%u), chunk_len=%u\n", topic, topic_len, chunk_len);
    char msg_template[128];
    if (strcmp(topic, TOPIC_ID_CONFIG) == 0) {
        // received answer during Id negotiation
        snprintf(msg_template, sizeof(msg_template), "%s %d approved", NODE_TYPE, candidateID);
        if (strcmp((const char *) chunk, msg_template) == 0) {
            // controlled accepted Id proposal
            tagId = candidateID;
            mqtt_unsubscribe(&conn, NULL, TOPIC_ID_CONFIG);

            // it's not subscribed to anything, but the state is used for publishing things
            state = STATE_PRESUBSCRIBED;
            boot = BOOT_COMPLETED;
            printf("Heartsensor: State Presubscribed & Boot Completed\n");
            //printf("boot %d, state %d", boot, state);
        } else {
            snprintf(msg_template, sizeof(msg_template), "%s %d denied", NODE_TYPE, candidateID);
            if (strcmp((const char *) chunk, msg_template) == 0) {
                // controlled rejected Id proposal
                boot = BOOT_ID_DENIED;
                printf("Heartsensor: Id Denied \n");
            }
        }
    }
}

/*---------------------------------------------------------------------------*/
static void mqtt_event(struct mqtt_connection *m, mqtt_event_t event, void *data) {
    switch (event) {
        case MQTT_EVENT_CONNECTED: {
            printf("Heartsensor: state connected \n");
            state = STATE_CONNECTED;
            break;
        }
        case MQTT_EVENT_DISCONNECTED: {
            printf("MQTT Disconnect. Reason %u\n", *((mqtt_event_t *) data));
            state = STATE_DISCONNECTED;
            printf("Heartsensor: state disconnected \n");
            process_poll(&mqtt_client_process);
            break;
        }
        case MQTT_EVENT_PUBLISH: {
            msg_ptr = data;
            pub_handler(msg_ptr->topic, strlen(msg_ptr->topic), msg_ptr->payload_chunk, msg_ptr->payload_length);
            break;
        }
        case MQTT_EVENT_SUBACK: {
#if MQTT_311
            mqtt_suback_event_t *suback_event = (mqtt_suback_event_t *)data;
            if(suback_event->success) {
              printf("Application is subscribed to topic successfully\n");
            } else {
              printf("Application failed to subscribe to topic (ret code %x)\n", suback_event->return_code);
            }
#else
            printf("Application is subscribed to topic successfully\n");
#endif
            break;
        }
        case MQTT_EVENT_UNSUBACK: {
            printf("Application is unsubscribed to topic successfully\n");
            break;
        }
        case MQTT_EVENT_PUBACK: {
            printf("Publishing complete.\n");
            break;
        }
        default:
            printf("Application got a unhandled MQTT event: %i\n", event);
            break;
    }
}

static bool have_connectivity(void) {
    if (uip_ds6_get_global(ADDR_PREFERRED) == NULL ||
        uip_ds6_defrt_choose() == NULL) {
        return false;
    }
    return true;
}


/*---------------------------------------------------------------------------*/
PROCESS_THREAD(mqtt_client_process, ev, data) {
    PROCESS_BEGIN();


	counter = 0;
    printf("MQTT Heart Sensor Process\n");
    boot = BOOT_NOT_STARTED;
    // Initialize the ClientID as MAC address
    snprintf(client_id, BUFFER_SIZE, "%02x%02x%02x%02x%02x%02x",
             linkaddr_node_addr.u8[0], linkaddr_node_addr.u8[1],
             linkaddr_node_addr.u8[2], linkaddr_node_addr.u8[5],
             linkaddr_node_addr.u8[6], linkaddr_node_addr.u8[7]);

    // Broker registration
    mqtt_register(&conn, &mqtt_client_process, client_id, mqtt_event,
                  MAX_TCP_SEGMENT_SIZE);
    state = STATE_INIT;
    printf("Heartsensor: state init \n");
    // Initialize periodic timer to check the status
    etimer_set(&periodic_timer, DEFAULT_PUBLISH_INTERVAL);
	etimer_set(&sub_timer, DEFAULT_PUBLISH_INTERVAL);
    rgb_led_set(RGB_LED_RED);
    boot = BOOT_INIT;
    /* Main loop */
    printf("Heartsensor boot %d \n", boot);
    while (1) {

        PROCESS_YIELD();

	    if (etimer_expired(&sub_timer)) {
            if(state == STATE_PRESUBSCRIBED){
                      state = STATE_SUBSCRIBED;
                      printf("Heartsensor: State Subscribed\n");
                      printf("Heartsensor boot %d state %d \n", boot, state);
            }
        }
        if ((ev == PROCESS_EVENT_TIMER && data == &periodic_timer) || ev == PROCESS_EVENT_POLL) {

            if (state == STATE_INIT && have_connectivity()) {
                state = STATE_NET_OK;
                printf("Heartsensor: state net ok \n");
            }

            if (state == STATE_NET_OK) {
                // Connect to MQTT server
                printf("Connecting!\n");
                memcpy(broker_address, broker_ip, strlen(broker_ip));
                mqtt_connect(&conn, broker_address, DEFAULT_BROKER_PORT, (DEFAULT_PUBLISH_INTERVAL * 3) / CLOCK_SECOND,
                             MQTT_CLEAN_SESSION_ON);
                state = STATE_CONNECTING;
	            printf("Heartsensor: state connecting \n");
                printf("Heartsensor boot %d \n", boot);
            }

            if (state == STATE_CONNECTED) {
                if (boot == BOOT_INIT) {
                    // Subscribe to a topic
                    strcpy(sub_topic, TOPIC_ID_CONFIG);
                    printf("subtopic: %s\n", sub_topic);
                    statusId_config = mqtt_subscribe(&conn, NULL, sub_topic, MQTT_QOS_LEVEL_0);
                    printf("Subscribing to Id Config\n");
                    if (statusId_config == MQTT_STATUS_OUT_QUEUE_FULL) {
                        LOG_ERR("Tried to subscribe but command queue was full!\n");
                        PROCESS_EXIT();
                    }
                    candidateID = 1 + (int) random_rand() % 100;
                    boot = BOOT_ID_NEGOTIATION;
                }
                if (boot == BOOT_ID_DENIED) {
                    printf("Heartsensor %d: Id Denied\n", candidateID);
                    // Id negotiation failed, must repeat it
                    candidateID = 1 + (int) random_rand() % 100;
                    boot = BOOT_ID_NEGOTIATION;
                    counter=0;
                    printf("Heartsensor boot: %d\n", boot);
                }
                if (boot == BOOT_ID_NEGOTIATION) {
                    if((counter == 0) || (counter == 1)){
                        if(counter == 0){
                            printf("Heartsensor %d: Publishing candidate_id \n", candidateID);
                            // id negotiation: ask controller for Id approval
                            sprintf(app_buffer, "%s %d awakens", NODE_TYPE, candidateID);
                            sprintf(pub_topic, "%s", TOPIC_ID_CONFIG);
                            printf("%s \n", app_buffer);
                            counter =1;
                        }
                        status_Publish = mqtt_publish(&conn, NULL, pub_topic, (uint8_t *) app_buffer, strlen(app_buffer), MQTT_QOS_LEVEL_0,
                                MQTT_RETAIN_OFF);
                        if (status_Publish == 0) {
                            counter = 2;
                            etimer_reset(&sub_timer);
                        }
                        else{ printf("Wait to publish because the Client queue is full \n");}
                    }
                    if ( counter >= 2) {
                    // published candidate_id, waiting for answer
                        counter ++;
                        printf("Node %d still waiting for id negotiation \n", candidateID);
                        if (counter > 5) {
                            // wait is too long. controller probably forgot about me.
                            counter = 0;
                            printf("Exceeded idle time for %d; restarting id negotiation \n", candidateID);
                        }
                    }
                }

            }
            if ((boot == BOOT_COMPLETED) && (state == STATE_SUBSCRIBED)) {
                // Publish periodic sensor data

                // simulate random change in heartbeat
                heartbeat = (int) random_rand() % 150;
                heartbeat += 40;
                LOG_INFO("Heartbeat %d value: %d\n", tagId, heartbeat);

                sprintf(pub_topic, "%s", TOPIC_SENSOR_DATA);

                sprintf(app_buffer, PUBLISH_MSG_TEMPLATE, tagId, heartbeat);

                mqtt_publish(&conn, NULL, pub_topic, (uint8_t *) app_buffer, strlen(app_buffer), MQTT_QOS_LEVEL_0,
                             MQTT_RETAIN_OFF);
            }
            if (state == STATE_DISCONNECTED) {
                printf("Heartsensor %d: disconnected \n", tagId);
                LOG_ERR("Disconnected from MQTT broker\n");
                boot = BOOT_INIT;
                rgb_led_set(RGB_LED_RED);
                // Recover from error
                state = STATE_INIT;
                counter=0;
            }
            etimer_set(&periodic_timer, DEFAULT_PUBLISH_INTERVAL);
        }
    }
    PROCESS_END();
}
/*---------------------------------------------------------------------------*/
