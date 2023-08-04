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

/* Log configuration */
#include "coap-log.h"

#include "dev/leds.h"
#include "dev/rgb-led/rgb-led.h"

#define LOG_MODULE "App"
#define LOG_LEVEL  LOG_LEVEL_APP

//TODO DA DEFINIRE INDIRIZZO SERVER
#define SERVER_EP "coap://[fd00::202:2:2:2]:5683"
char *service_url = "/hello";

#define STATE_INIT            0
#define STATE_REGISTERING      1
#define STATE_REGISTERED       2
int status = 0;
int self_id;
char *res_name;
extern coap_resource_t res_status;
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

/*---------------------------------------------------------------------------*/
PROCESS(actuator_node, "actuator_node");
AUTOSTART_PROCESSES(&actuator_node);

/* This function is will be passed to COAP_BLOCKING_REQUEST() to handle responses. */
void client_chunk_handler(coap_message_t *response)
{
	const uint8_t *chunk;

	if(response == NULL) {
		LOG_INFO("Request timed out");
		return;
	}
	node_registered = true;
	int len = coap_get_payload(response, &chunk);
	LOG_INFO("|%.*s \n", len, (char *)chunk);

    if (status == STATE_REGISTERING) {
        status = STATE_REGISTERED;
    }

}


PROCESS_THREAD(actuator_node, ev, data)
{
  static coap_endpoint_t serverCoap;
  static coap_message_t request[1];

  PROCESS_BEGIN();
  LOG_INFO("Starting actuator node\n");
  coap_activate_resource(&res_status, "hatch");
  coap_endpoint_parse(SERVER_EP, strlen(SERVER_EP), &serverCoap);
  coap_init_message(request, COAP_TYPE_CON, COAP_GET, 0);  
  coap_set_header_uri_path(request, service_url);

  rgb_led_set(RGB_LED_GREEN);

  
  while(1) {
    if(status == STATE_INIT){
    // In a real application, MAC address is to be used instead of random
        self_id = 1 + (int) random_rand() % 500;
        char msg[32];
        snprintf(msg, sizeof(msg),"food_%d", self_id);

        status = STATE_REGISTERING;
        coap_set_payload(request, (uint8_t *) msg, sizeof(msg) - 1);
        COAP_BLOCKING_REQUEST(&serverCoap, request, client_chunk_handler);
        LOG_INFO("--Node Registering--\n");
        }
    PROCESS_WAIT_EVENT();

    //WORK PHASE: there is no actuator in the simulation
  }

  PROCESS_END();
}