#ifndef BHOLANATH_H
#define BHOLANATH_H

	#include "stm32f4xx.h"
	#include<stdint.h>
	#include<stdio.h>
	#include<string.h>
	#include<stdlib.h>
	//#include<math.h>


	void vSetupUART(void);
	void vSetupButtonAndLED(void);
	void vBlinkLED(unsigned int count);


	void vPrint_Msg(char *msg);
	void vReadMsg(uint16_t* Msg, unsigned int length);

#endif
