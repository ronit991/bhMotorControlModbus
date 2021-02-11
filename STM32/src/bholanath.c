#include"bholanath.h"

void vReadMsg(uint16_t* Msg, unsigned int length)
{
	uint16_t currentChar;
	for(int i = 0; i <= length; i++)
	{
		while( USART_GetFlagStatus(USART2, USART_FLAG_RXNE) != SET);
		currentChar = USART_ReceiveData(USART2);
		if( (currentChar == 13) || (currentChar == 10) )
		{
			break;		// Stop reading when a NL or CR character is received
		}
		if( (currentChar == 98) || (currentChar == 39) )
		{				// Ignore character b and ' (single quote char). These are sent by python while encoding the data,
			i--;		// so we don't need them
		}
		else
			Msg[i] = (currentChar - 48);	// Zero character has ASCII value = 48. Subtracting 48 gives us the data in numeric form.
	}
}

void vPrint_Msg(char *msg)
{
	for(unsigned int i = 0; i<strlen(msg); i++)
	{
		while( USART_GetFlagStatus(USART2, USART_FLAG_TXE) != SET );		// Wait for transmission complete
		USART_SendData(USART2, msg[i]);										// Send a character over UART
	}
}

void vSetupUART(void)
{
	//	PA2 is USART2 Tx, PA3 is USART2 Rx
	//	1. Enable UART2 and GPIOA Peripheral Clock
	RCC_APB1PeriphClockCmd(RCC_APB1Periph_USART2, ENABLE);
	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);

	// GPIO Configuration for UART pins
	GPIO_InitTypeDef UART_GPIO_Pins;
	memset(&UART_GPIO_Pins, 0, sizeof(UART_GPIO_Pins));			//	Reset all variables of the structure before initializing
	UART_GPIO_Pins.GPIO_Mode = GPIO_Mode_AF;
	UART_GPIO_Pins.GPIO_Pin = GPIO_Pin_2 | GPIO_Pin_3;
	UART_GPIO_Pins.GPIO_PuPd = GPIO_PuPd_UP;

	// Initialize UART pins with above configuration.
	GPIO_Init(GPIOA, &UART_GPIO_Pins);
	// Configure the pins to be used in Alternate Function Mode
	GPIO_PinAFConfig(GPIOA, GPIO_PinSource2, GPIO_AF_USART2);
	GPIO_PinAFConfig(GPIOA, GPIO_PinSource3, GPIO_AF_USART2);

	// Configuration for USART2 Peripheral
	USART_InitTypeDef UART2config;
	memset(&UART2config, 0, sizeof(UART2config));			    //	Reset all variables of the structure before initializing
	UART2config.USART_BaudRate = 9600;
	UART2config.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
	UART2config.USART_Mode = USART_Mode_Rx | USART_Mode_Tx;
	UART2config.USART_Parity = USART_Parity_No;
	UART2config.USART_StopBits = USART_StopBits_1;
	UART2config.USART_WordLength = USART_WordLength_8b;
	USART_Init(USART2, &UART2config);

	/*
	// Enable the Interrupt
	USART_ITConfig(USART2, USART_IT_RXNE, ENABLE);
	// Enable interrupt reception on this irq num
	NVIC_EnableIRQ(USART2_IRQn);*/

	// Enable the USART2 Peripheral
	USART_Cmd(USART2, ENABLE);
}

void vSetupButtonAndLED(void)
{
	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOA, ENABLE);
	RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOC, ENABLE);

	// Configure On-Board LED
	GPIO_InitTypeDef led;
	led.GPIO_Mode = GPIO_Mode_OUT;
	led.GPIO_OType = GPIO_OType_PP;
	led.GPIO_Pin = GPIO_Pin_5;
	GPIO_Init(GPIOA, &led);

	// Configure On-Board Button
	GPIO_InitTypeDef button;
	button.GPIO_Mode = GPIO_Mode_IN;
	//button.GPIO_PuPd = GPIO_PuPd_UP;
	button.GPIO_Pin = GPIO_Pin_13;
	GPIO_Init(GPIOC, &button);

	// Interrupt Configuration
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_SYSCFG, ENABLE);
	SYSCFG_EXTILineConfig(EXTI_PortSourceGPIOC, EXTI_PinSource13);

	// Configure EXTI settings in SYSCFG
	EXTI_InitTypeDef EXTI_h;		// EXTI configuration structure
	EXTI_h.EXTI_Mode = EXTI_Mode_Interrupt;
	EXTI_h.EXTI_Trigger = EXTI_Trigger_Rising;
	EXTI_h.EXTI_Line = EXTI_Line13;
	EXTI_h.EXTI_LineCmd = ENABLE;
	EXTI_Init(&EXTI_h);

	NVIC_SetPriority(EXTI15_10_IRQn, 6);

	// Configure NVIC
	NVIC_EnableIRQ(EXTI15_10_IRQn);
}

void vBlinkLED(unsigned int count)
{
	for(int i = 0; i < (2*count); i++)
	{
		GPIO_ToggleBits(GPIOA, GPIO_Pin_5);
		for(int j = 0; j < 10000000; j++);
	}
	GPIO_ResetBits(GPIOA, GPIO_Pin_5);
}
