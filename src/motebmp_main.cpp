// *************************************************************************************************************
//                                        WeatherShield sample sketch
// *************************************************************************************************************
// This sketch does periodic reads from a Moteino Weather Shield BMP180 and Si7021 sensors and displays
// information like this (real sample):
//
//        ************ Si7021 *********************************
//        C: 2389   F: 7500   H: 36%   DID: 21  BATT: 1015
//        ************ BMP180 *********************************
//        provided altitude: 218 meters, 716 feet
//        C: 24.14    F:75.44
//        abs pressure: 992.23 mb, 29.30 inHg
//        relative (sea-level) pressure: 1018.31 mb, 30.07 inHg
//        computed altitude: 218 meters, 716 feet
//
//   You can also read the battery reading from the VIN pin through a resistor divider (VIN - 4.7K + 10K -GND).
//   This is enabled through a P-mosfet that is turned ON through A3. To save power, you only need to turn this 
//   circuit ON when you need a reading. To turn ON set A3 to OUTPUT and LOW. To turn it OFF for power saving set
//   A3 to INPUT (this makes A3 HIGH-Z).
// *************************************************************************************************************
#include "Arduino.h"

#include <SFE_BMP180.h>    //get it here: https://github.com/LowPowerLab/SFE_BMP180
#include <SI7021.h>        //get it here: https://github.com/LowPowerLab/SI7021
#include <Wire.h>

#ifdef __AVR_ATmega1284P__
  #define IS_RFM69HW    //uncomment only for RFM69HW! Leave out if you have RFM69W!
  #define LED           15 // Moteino MEGAs have LEDs on D15
//  #define FLASH_SS      23 // and FLASH SS on D23
#else
  #define LED           9 // Moteinos have LEDs on D9
//  #define FLASH_SS      8 // and FLASH SS on D8
#endif

int brightness = 0;    // how bright the LED is
int fadeAmount = 5;    // how many points to fade the LED by

SI7021 sensor;
SFE_BMP180 pressure;
#define ALTITUDE 64.0 // Altitude in meters

void read_sensors(char input);
void fadeloop();

// 
void setup() {
  pinMode(A7, INPUT);
  Serial.begin(115200);
  sensor.begin();

  // declare pin 9 to be an output:
  pinMode(LED, OUTPUT);
  
  if (!pressure.begin())
  {
    // Oops, something went wrong, this is usually a connection problem,
    // see the comments at the top of this sketch for the proper connections.

    Serial.println("-1: BMP180 init fail\n\n");
    while(1) {
    	fadeloop();
 	}
  }
  else
    Serial.println("BMP180 init OK");
}

//
void loop() {
	
	if (Serial.available() > 0)
	{
		char input = Serial.read();
//		Serial.println(input);
		read_sensors( input );
	}
}

// ------------

void read_sensors(char input)
{
	int Si_hum  = sensor.getHumidityPercent();
	int metric = (input =='m' || input =='M');
	int simple = (input < 'a');

#if 0
	int Si_temp = 0;
	if (metric)
		Si_temp = sensor.getCelsiusHundredths();
	else
		Si_temp = sensor.getFahrenheitHundredths();
#endif
	
	//
	Serial.print( Si_hum ); if (!simple) Serial.print( "%H" );
	Serial.print("\t");
	
	char status;
	double T,P,p0;

  // If you want to measure altitude, and not pressure, you will instead need
  // to provide a known baseline pressure. This is shown at the end of the sketch.
  // You must first get a temperature measurement to perform a pressure reading.
  // Start a temperature measurement:
  // If request is successful, the number of ms to wait is returned.
  // If request is unsuccessful, 0 is returned.
	status = pressure.startTemperature();
	if (status == 0)
	{
	  Serial.println("-1: startTemp fail");
	  return;
	}
  
	// Wait for the measurement to complete:
	delay(status);

    // Retrieve the completed temperature measurement:
    // Note that the measurement is stored in the variable T.
    // Function returns 1 if successful, 0 if failure.

    status = pressure.getTemperature(T);
    if (status == 0)
    {
    	Serial.println("-1: getTemp fail");
    	return;
    }

	// Start a pressure measurement:
	// The parameter is the oversampling setting, from 0 to 3 (highest res, longest wait).
	// If request is successful, the number of ms to wait is returned.
	// If request is unsuccessful, 0 is returned.
	
	status = pressure.startPressure(3);
	if (status == 0)
	{
	  Serial.println("-1: startPressure fail");
	  return;
	}
	
	// Wait for the measurement to complete:
	delay(status);
	
	// Retrieve the completed pressure measurement:
	// Note that the measurement is stored in the variable P.
	// Note also that the function requires the previous temperature measurement (T).
	// (If temperature is stable, you can do one temperature measurement for a number of pressure measurements.)
	// Function returns 1 if successful, 0 if failure.
	
	status = pressure.getPressure(P,T);
	if (status == 0)
	{
		Serial.println("-1: getPressure fail");
		return;
	}
	//
	
	if (metric)
	{
//		Serial.print( Si_temp ); Serial.print( " C\t");

		Serial.print(T,3); if (!simple) Serial.print(" C");
		Serial.print("\t");

		// Print out the measurement:
		Serial.print(P,3); if (!simple) Serial.print(" mb_abs");
		Serial.print("\t");

		// The pressure sensor returns abolute pressure, which varies with altitude.
		// To remove the effects of altitude, use the sealevel function and your current altitude.
		// This number is commonly used in weather reports.
		// Parameters: P = absolute pressure in mb, ALTITUDE = current altitude in m.
		// Result: p0 = sea-level compensated pressure in mb
		
		p0 = pressure.sealevel(P,ALTITUDE); // we're at 1655 meters (Boulder, CO)
		Serial.print(p0,3); if (!simple) Serial.print(" mb_rel");
		Serial.print("\t");
	}
	else
	{
//		Serial.print( Si_temp ); Serial.print( " F\t");

		Serial.print((9.0/5.0)*T+32.0,3); if (!simple) Serial.print(" F");
		Serial.print("\t");

		// Print out the measurement:
		Serial.print(P*0.0295333727,3); if (!simple) Serial.print(" inHg_abs");
		Serial.print("\t");
		
		// The pressure sensor returns abolute pressure, which varies with altitude.
		// To remove the effects of altitude, use the sealevel function and your current altitude.
		// This number is commonly used in weather reports.
		// Parameters: P = absolute pressure in mb, ALTITUDE = current altitude in m.
		// Result: p0 = sea-level compensated pressure in mb
		
		p0 = pressure.sealevel(P,ALTITUDE); // we're at 1655 meters (Boulder, CO)
		Serial.print(p0*0.0295333727,3); if (!simple) Serial.print(" inHg_rel");
		Serial.print("\t");
	}
	Serial.println();
}

// the loop routine runs over and over again forever:
void fadeloop() {
  // set the brightness of pin 9:
  analogWrite(LED, brightness);

  // change the brightness for next time through the loop:
  brightness = brightness + fadeAmount;

  // reverse the direction of the fading at the ends of the fade:
  if (brightness == 0 || brightness == 255) {
    fadeAmount = -fadeAmount ;
  }
  // wait for 30 milliseconds to see the dimming effect
  delay(20);
}

