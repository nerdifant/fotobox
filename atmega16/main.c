/*
 *
 */ 

#include <util/delay.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include "light_ws2812.h"

#define ledCountIn 24	// Number of LED pixels in the inner ring.
#define ledCountOut 32	// Number of LED pixels in the outer ring.
#define numPixels 96	// Virtual number of LED pixels.
#define	brightness 8
#define speed 50

struct cRGB led[ledCountIn+ledCountOut];
int rainbowLastPos = 0;
int mode = 1;
	/*
	 * 0 = off
	 * 1 = rainbow
	 * 2 = countdown
	 * 3 = loading
	 * 4 = finished
	 * 5 = 
	 * 6 = 
	 * 7 = error
	*/

void setPixelColorCycle(int pos, struct cRGB color, int innerRing, int outerRing){
	pos = (pos + 44) % numPixels;
	color.r=color.r*brightness/255;
	color.g=color.g*brightness/255;
	color.b=color.b*brightness/255;
	// Inner ring
	if (innerRing && (pos % 4) == 0) { led[pos/4] = color; }
	// Outer ring
	if (outerRing && (pos % 3) == 0) { led[ledCountIn + pos/3] = color; }
}

void setRingColor(struct cRGB color, int innerRing, int outerRing){
	for (int i=0; i<numPixels;i++) { setPixelColorCycle(i, color, innerRing, outerRing); }
}

void applyLED(void){
	ws2812_sendarray((uint8_t *)led,(ledCountIn*ledCountOut)*3);
}


struct cRGB wheel(int pos) {
	// Generate rainbow colors across 0-255 positions.
	struct cRGB color;
	if (pos<85){
		color.r=pos*3;
		color.g=255-pos*3;
		color.b=0;
	} else {
		if (pos<170) {
			pos-=85;
		 	color.r=255-pos*3;
			color.g=0;
			color.b=pos*3;
		} else {		
      			pos-=170;
		 	color.r=0;
			color.g=pos*3;
			color.b=255-pos*3;
	}}
	return color;
}

struct cRGB defColor(int r, int g, int b) {
	struct cRGB color;
	color.r = r;
	color.g = g;
	color.b = b;
	return color;
}

void rainbow(void) {
	rainbowLastPos = (rainbowLastPos + 1) % numPixels;
	for (int i=0; i<numPixels; i++) { setPixelColorCycle(i, wheel(((int)(i*256/numPixels + rainbowLastPos*256/numPixels)) & 255), 1, 1); }
}

void countdown(struct cRGB color) {
	// Countdown
	for (int i=0; i<ledCountIn; i++) {
		setPixelColorCycle(numPixels - (i * 4), defColor(0, 0, 0), 1, 0);
		if (i % 2 == 0) { setRingColor(color, 0, 1);
      		} else { setRingColor(defColor(0, 0, 0), 0, 1); }
		applyLED();
		_delay_ms(50*speed);
      	}

	// Flash
	setRingColor(defColor(255, 255, 255), 1, 1); // All lights on
	applyLED();
	_delay_ms(100*speed);

	// Start loading
	rainbowLastPos = 0;
	mode = 3;
}

void loading(void) {
	// Waiting Rainbow
	rainbowLastPos = (rainbowLastPos + 1) % numPixels;
	setPixelColorCycle(rainbowLastPos, defColor(0, 0, 0), 1, 0);
	setPixelColorCycle(numPixels-rainbowLastPos, defColor(0, 0, 0), 0, 1);
	for (int j=0; j<20; j++) {
		setPixelColorCycle(rainbowLastPos+1+j, wheel((int)((rainbowLastPos+1+j) * 256 / numPixels) & 255), 1, 0);
		setPixelColorCycle(numPixels-rainbowLastPos-1-j, wheel((int)((numPixels-rainbowLastPos-1-j) * 256 / numPixels) & 255), 0, 1);
	}
}

void finish(void) {
	for (int j=0; j<numPixels-21; j++){
		int i = (rainbowLastPos+21+j) % numPixels;
		setPixelColorCycle(i, wheel((int)(i * 256 / numPixels) & 255), 1, 0);
		setPixelColorCycle(numPixels-i, wheel((int)((numPixels-i) * 256 / numPixels) & 255), 0, 1);
		_delay_ms(speed);
		applyLED();
	}

	for (int i=0; i<3; i++) {
		setRingColor(defColor(0, 0, 0), 1, 1);		_delay_ms(100*speed);	applyLED();
		setRingColor(defColor(0, 255, 0), 1, 1);	_delay_ms(100*speed);	applyLED();
	}

	mode = 1;
}

void error(void) {
	if (rainbowLastPos > 0) {
		setRingColor(defColor(0, 0, 0), 1, 1);
		rainbowLastPos = 0;
	} else {
		setRingColor(defColor(255, 0, 0), 1, 1);
		rainbowLastPos = 1;
	}
	_delay_ms(99*speed);
}

int main(void) {
	DDRC = 0x00;	// Sets PINC 0-7 to Input
	DDRA = 0xff;	// Sets PINA 0-7 to Output
	PORTA = 0x00;	// Sets all pins of PINA to zero

	while (1) {
		switch((PINC & 0x03)) {
			case 0:	if (mode == 2 || mode == 3) { mode = 4; }
				else { mode = 1; }
				break;
			case 1: if (mode == 1) { mode = 2; }
				break;
			case 2: mode = 7;
				break;
			case 3: mode = 0;
				break;
		}
		switch(mode) {
			case 0:	setRingColor(defColor(0, 0, 0), 1, 1);
				break;
			case 1: rainbow();
				break;
			case 2: countdown(defColor(0, 255, 0));
				break;
			case 3: loading();
				break;
			case 4: finish();
				break;
			case 7: error();
				break;
		}
		applyLED();
		_delay_ms(speed);
	}

	return 0;
}
