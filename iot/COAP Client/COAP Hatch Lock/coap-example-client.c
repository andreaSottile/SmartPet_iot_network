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
#include "dev/etc/rgb-led/rgb-led.h"
#include "dev/button-hal.h"

/* Log configuration */
#include "app_var.h"
#include "coap-log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL  LOG_LEVEL_APP

//TODO DA DEFINIRE INDIRIZZO SERVER
#define SERVER_EP "coap://[fd00::202:2:2:2]:5683"
char *service_url = "/hello";

bool node_registered = false;
int status = 0;
char *res_name
extern coap_resource_t res_status;

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
  possible_ID= 1 + (int) random_rand() % 100;
  const char msg[] = "hatch_" + possible_ID;
  coap_set_payload(request, (uint8_t *)msg, sizeof(msg) - 1);
  COAP_BLOCKING_REQUEST(&serverCoap, request, client_chunk_handler);
  LOG_INFO("--Node Registered--\n");
  rgb_led_set(RGB_LED_GREEN);

  
  while(1) {
    PROCESS_WAIT_EVENT();
     
    //TODO GESTIONE CLIENT
  }

  PROCESS_END();
}