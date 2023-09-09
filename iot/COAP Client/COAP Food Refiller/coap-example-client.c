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
 * 3. Neither the name of the Institute nor the names of its contributors
 *    may be used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE INSTITUTE AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE INSTITUTE OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 * This file is part of the Contiki operating system.
 */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include "contiki.h"
#include "coap-engine.h"
#include "sys/etimer.h"
#include "coap-blocking-api.h"
#include "random.h"
#include "node-id.h"
#include "os/dev/serial-line.h"
#include "dev/button-hal.h"
#include "dev/leds.h"
#include "dev/rgb-led/rgb-led.h"

/* Log configuration */
#include "coap-log.h"
#define LOG_MODULE "App"
// #define LOG_LEVEL  LOG_LEVEL_APP
#define LOG_LEVEL  LOG_LEVEL_RPL

#define SERVER_EP "coap://[fd00::1]:5683"
#define TOGGLE_INTERVAL    (10 * CLOCK_SECOND)


char *service_url = "hello";

static uint8_t state;
#define STATE_INIT            0
#define STATE_REGISTERING      1
#define STATE_REGISTERED       2
int self_id;
char *res_name;
extern coap_resource_t res_status;

PROCESS(actuator_node,"actuator_node");
AUTOSTART_PROCESSES(&actuator_node);
static struct etimer et;

/* This function is will be passed to COAP_BLOCKING_REQUEST() to handle responses. */
void client_chunk_handler(coap_message_t *response) {
    const uint8_t *chunk;

    if (response == NULL) {
        LOG_INFO("Request timed out");
        printf("risposta null \n");
        return;
    }
    printf("dopo response \n");
    int len = coap_get_payload(response, &chunk);
    LOG_INFO("|%.*s \n", len, (char *) chunk);

    if (state == STATE_REGISTERING){
        state = STATE_REGISTERED;
        printf("\n--state Registered--\n");
        }
}


PROCESS_THREAD(actuator_node, ev, data) {
    static coap_endpoint_t serverCoap;
    static coap_message_t request[1];
    button_hal_button_t *button;
    button = button_hal_get_by_index(0);
    PROCESS_BEGIN();

    LOG_INFO("Starting actuator node\n");
    char msg[32];
    state = STATE_INIT;
    printf("\n--state Registered--\n");
    coap_activate_resource(&res_status, "food");
    etimer_set(&et, TOGGLE_INTERVAL);
    rgb_led_set(RGB_LED_GREEN);

    if(button) {
        // Prints all the information about the button
        printf("%s on pin %u with ID=0, Logic=%s, Pull=%s\n",
        BUTTON_HAL_GET_DESCRIPTION(button), button->pin,
        button->negative_logic ? "Negative" : "Positive",
        button->pull == GPIO_HAL_PIN_CFG_PULL_UP ? "Pull Up" : "Pull Down");
       }
    while (1) {
        PROCESS_YIELD();
        printf("\n--state in yield %d--\n", state);
        if(ev == button_hal_press_event) {
            button = (button_hal_button_t *)data; // In the data field there is pointer to the button
            // DO ANY ACTION
            printf("Press event (%s)\n", BUTTON_HAL_GET_DESCRIPTION(button));
            printf("\n--state in press button %d--\n", state);
            }
        if(ev == button_hal_release_event) {
            button = (button_hal_button_t *)data;
            printf("Release event (%s)\n", BUTTON_HAL_GET_DESCRIPTION(button));
            printf("\n--state in release button %d--\n", state);
            self_id = 501 + (int) random_rand() % 500;
            snprintf(msg, sizeof(msg),"food_%d", self_id);
            printf("Food Actuator %s: Communicating id \n", self_id);
            state = STATE_REGISTERING;
            coap_endpoint_parse(SERVER_EP, strlen(SERVER_EP), &serverCoap);
            coap_init_message(request, COAP_TYPE_CON, COAP_GET, 0);
            coap_set_header_uri_path(request, service_url);
            coap_set_payload(request, (uint8_t *) msg, sizeof(msg) - 1);
            COAP_BLOCKING_REQUEST(&serverCoap, request, client_chunk_handler);}
        if(etimer_expired(&et)) {
            etimer_reset(&et);
            printf("\n--state on periodic timer %d--\n", state);
            if((state == STATE_INIT)||(state == STATE_REGISTERING)){
            // In a real application, MAC address is to be used instead of random
            printf("Food Actuator: init \n");
            self_id = 501 + (int) random_rand() % 500;
            snprintf(msg, sizeof(msg),"food_%d", self_id);
            printf("Food Actuator %s: Communicating id \n", self_id);
            state = STATE_REGISTERING;
            coap_endpoint_parse(SERVER_EP, strlen(SERVER_EP), &serverCoap);
            coap_init_message(request, COAP_TYPE_CON, COAP_GET, 0);
            coap_set_header_uri_path(request, service_url);
            coap_set_payload(request, (uint8_t *) msg, sizeof(msg) - 1);
            COAP_BLOCKING_REQUEST(&serverCoap, request, client_chunk_handler);
            LOG_INFO("--Node Registering--\n");
            printf("dopo blocking request \n");
        }
            if(state == STATE_REGISTERED){
                char msg[32];
                    snprintf(msg, sizeof(msg),"food_%d", self_id);
                    coap_set_payload(request, (uint8_t *) msg, sizeof(msg) - 1);
                    COAP_BLOCKING_REQUEST(&serverCoap, request, client_chunk_handler);
                    LOG_INFO("--%d Keepalive--\n", self_id);
            }
            printf("\n--reset Timer--\n");

        }
        //WORK PHASE: there is no actuator in the simulation
    }

    PROCESS_END();
}