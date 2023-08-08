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
#include <string.h>
#include "../app_var.h"
#include "coap-engine.h"
#include "contiki.h"
#include "dev/leds.h"
#include "os/dev/serial-line.h"
#include "coap-observe.h"
#include "dev/etc/rgb-led/rgb-led.h"


/* Log configuration */
#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_APP

static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);
static void res_event_handler(void);
static void res_post_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);
//TODO: VERIFICARE FUNZIONAMENTO

/*
 * A handler function named [resource name]_handler must be implemented for each RESOURCE.
 * A buffer for the response payload is provided through the buffer pointer. Simple resources can ignore
 * preferred_size and offset, but must respect the REST_MAX_CHUNK_SIZE limit for the buffer.
 * If a smaller block size is requested for CoAP, the REST framework automatically splits the data.
 */
EVENT_RESOURCE(res_status,
         "title=\"Status \" POST command=0|1|2;food;rt=\"status\"",
         res_get_handler,
         res_post_handler,
         NULL,
         NULL, 
		 res_event_handler);

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
  LOG_INFO("post");
  if((len = coap_get_post_variable(request, "command", &command))) {
    LOG_DBG("command_food_refiller %s\n", command);

    // 0 => close
    // 1 => watering 
    // 2 => recharging
    if(strncmp(command, "0", len) == 0) {
      LOG_INFO("0");
      rgb_led_set(RGB_LED_YELLOW);
      coap_set_status_code(response,VALID_2_03);
      status = 0;
      success = 1;
    } else if(strncmp(command, "1", len) == 0) {
      LOG_INFO("1");
      rgb_led_set(RGB_LED_GREEN);
      if(status == 0){
        coap_set_status_code(response,VALID_2_03);
        status = 1;
        success = 1;
      }
    } 
    else if(strncmp(command, "2", len) == 0) {
      LOG_INFO("2");
      rgb_led_set(RGB_LED_BLUE);
      if(status == 0){
        coap_set_status_code(response,VALID_2_03);
        status = 2;
        success = 1;
      }
    }
  } if(!success) {
    coap_set_status_code(response, BAD_REQUEST_4_00);
  }
}
