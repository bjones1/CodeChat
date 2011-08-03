
// "Copyright (c) 2008 Robert B. Reese, Bryan A. Jones, J. W. Bruce ("AUTHORS")"<br />
// All rights reserved.<br />
// &nbsp; (R. Reese, reese_AT_ece.msstate.edu, Mississippi State University)<br />
// &nbsp; (B. A. Jones, bjones_AT_ece.msstate.edu, Mississippi State University)<br />
// &nbsp; (J. W. Bruce, jwbruce_AT_ece.msstate.edu, Mississippi State University)<br />
// <br />
// Permission to use, copy, modify, and distribute this software and its
// documentation for any purpose, without fee, and without written agreement is
// hereby granted, provided that the above copyright notice, the following
// two paragraphs and the authors appear in all copies of this software.<br />
// <br />
// IN NO EVENT SHALL THE "AUTHORS" BE LIABLE TO ANY PARTY FOR
// DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT
// OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF THE "AUTHORS"
// HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.<br />
// <br />
// THE "AUTHORS" SPECIFICALLY DISCLAIMS ANY WARRANTIES,
// INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
// AND FITNESS FOR A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER IS
// ON AN "AS IS" BASIS, AND THE "AUTHORS" HAS NO OBLIGATION TO
// PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.<br />
// <br />
// Please maintain this header in its entirety when copying/modifying
// these files.

// This file provdies a solution to practicum 2. The program consists of two sections: configuration and body code.<br />

int i; // Dummy declaration to make the lexer happy
#include <pic24_all.h>
#include <dataXfer.h>

// <h2>Motors</h2>
// Use RB0 and RB1 to control motor direction
void config_motor_dir(void) {
  CONFIG_RB0_AS_DIG_OUTPUT();
  CONFIG_RB1_AS_DIG_OUTPUT();
}

// This enum gives directions for the motor, per the table below. set_motor_dir directly assigning these values to RB1:0 to set motor direction. <br />
enum { 
  MOTOR_STOPL = 0,   // stop with both outputs low
  MOTOR_CW,          // clockwise
  MOTOR_CCW,         // counterclockwise
  MOTOR_STOPH        // stop with both outputs high
};

// Specify the motor's direction. The speed is controlled separately
// by the PWM.<br />
void set_motor_dir(uint16_t u16_dir) { 
  // Make sure we've passed a valid motor direction 
  ASSERT(u16_dir <= MOTOR_STOPH);
  _RB0 = u16_dir & 1;
  _RB1 = (u16_dir & 2) >> 1;
}

// <h2>State machine</h2>
// The state machine is given below.<br />
// <img src="practicum2Summer2011_fsm.png" /><br />
// <br />
// This enum specifies the state machine state shown in the diagram above.<br />
typedef enum {
  MOTOR_ON_WFP,	// The motor is on, we're waiting for a pushbutton press (WFP)
  MOTOR_OFF_WFR,        // The motor is off, we're waiting for a pushbutton release (WFR)
  MOTOR_OFF_WFP,        // The motor is off, we're waiting for a pushbutton release (WFR)
  MOTOR_ON_WFR,         // The motor is on, we're waiting for a pushbutton release (WFR)
  MAX_STATE             // This specifies the maximum allowable value for the state. but is not a valid state.
} STATE;

// This stores the state. It's volatile so it can be accessed in the ISR and in main().
volatile STATE e_state = MOTOR_ON_WFP;

// This array assigns human-readable names to the states.
const char* apsz_state[MAX_STATE] = {
  "MOTOR_ON_WFP",
  "MOTOR_OFF_WFR",
  "MOTOR_OFF_WFP",
  "MOTOR_ON_WFR"
};

// <h3>Pushbutton</h3>
// Configure the pushbutton. Since it's a SPST connected between the PIC's
// pin and groud, enable a pullup and wait for the pullup to take effect
// before proceeding.<br />
void config_pb(void) {
  CONFIG_RB13_AS_DIG_INPUT();
  ENABLE_RB13_PULLUP();
  DELAY_US(1);
}

// Define a macro which is true when the pushbutton is pressed.
#define PB_PRESSED() (_RB13 == 0)

// <h3>LED</h3>
// The LED requires only a digital output.
void config_led(void) {
 CONFIG_RB9_AS_DIG_OUTPUT();
}

// Define it using _LAT, not _R, so it can be toggled.
#define LED (_LATB9)

// <h2>Pulse width modulation</h2>
// In thie section, timer 2 and the output compare module are used to
// produce a PWM waveform.
#ifndef PWM_PERIOD
#define PWM_PERIOD 1000 // desired period, in us
#endif

// Set up timer 2 to produce an interrupt every PWM_PERIOD us.
void  configTimer2(void) {
  T2CON = T2_OFF | T2_IDLE_CON | T2_GATE_OFF
          | T2_32BIT_MODE_OFF
          | T2_SOURCE_INT
          | T2_PS_1_8;
  PR2 = usToU16Ticks(PWM_PERIOD, getTimerPrescale(T2CONbits)) - 1;
  TMR2  = 0;       //clear timer2 value
  _T2IF = 0;
  _T2IP = 1;
  _T2IE = 1;    //enable the Timer2 interrupt
}


void configOutputCapture1(void) {
  T2CONbits.TON = 0;       //disable Timer when configuring Output compare
  CONFIG_OC1_TO_RP(14);        //map OC1 to RP14/RB14
  //assumes TIMER2 initialized before OC1 so PRE bits are set
  OC1RS = 0;  //initially off
  //turn on the compare toggle mode using Timer2
  OC1CON = OC_TIMER2_SRC |     //Timer2 source
           OC_PWM_FAULT_PIN_DISABLE;  //PWM, no fault detection
}

void _ISR _T2Interrupt(void) {
  _T2IF = 0;    //clear the timer interrupt bit

  if ( (e_state == MOTOR_ON_WFP) || (e_state == MOTOR_ON_WFR)) {
    int32_t i32_temp;
    //update the PWM duty cycle from the ADC value
    i32_temp = ADC1BUF0;  //use 32-bit value for range
    //compute new pulse width that is 0 to 99% of PR2
    // pulse width (PR2) * ADC/4096
    i32_temp = (((i32_temp - 2048)*PR2) >> 11);
    if (i32_temp >= 0) {
      OC1RS = i32_temp;  //update pulse width value
      set_motor_dir(MOTOR_CW);
    } else {
      OC1RS = -i32_temp;  //update pulse width value
      set_motor_dir(MOTOR_CCW);
    }
    SET_SAMP_BIT_ADC1();      //start sampling and conversion
  }

  // State machine
  switch (e_state) {
    case MOTOR_ON_WFP :
      if (PB_PRESSED()) {
        e_state = MOTOR_OFF_WFR;
        OC1RS = 0;
      }
      break;

    case MOTOR_OFF_WFR :
      if (!PB_PRESSED()) {
        e_state = MOTOR_OFF_WFP;
      }
      break;

    case MOTOR_OFF_WFP :
      if (PB_PRESSED()) {
        e_state = MOTOR_ON_WFR;
      }
      break;

    case MOTOR_ON_WFR :
      if (!PB_PRESSED()) {
        e_state = MOTOR_ON_WFP;
      }
      break;

    default :
      ASSERT(0);
  }
}

/// Indexes of all the variables to be transferred.
enum { U32_PW_NDX, OC1RS_NDX, ADC1BUF0_NDX };


int main(void) {
  uint32_t u32_pw;
  STATE e_last_state = MAX_STATE;

  // Initialize
  configBasic(HELLO_MSG);
  initDataXfer();

  // All variables received by the PIC must be specified.
  // Params:  Index         Variable  PC can change  Format  Description
  SPECIFY_VAR(U32_PW_NDX,   u32_pw,   FALSE,         "%u",   "PWM pulse width (us)");
  SPECIFY_VAR(OC1RS_NDX,    OC1RS,    FALSE,         "%hu",  "Raw PWM value");
  SPECIFY_VAR(ADC1BUF0_NDX, ADC1BUF0, FALSE,         "%hu",  "Raw ADC value");

  // Configure motors
  configTimer2();
  configOutputCapture1();
  CONFIG_AN0_AS_ANALOG();
  configADC1_ManualCH0( ADC_CH0_POS_SAMPLEA_AN0, 31, 1 );
  SET_SAMP_BIT_ADC1();      //start sampling and conversion
  T2CONbits.TON = 1;       //turn on Timer2 to start PWM
  config_motor_dir();

  config_pb();
  config_led();

  // Report results only
  while (1) {
    u32_pw = ticksToUs(OC1RS, getTimerPrescale(T2CONbits));
    sendVar(U32_PW_NDX);
    sendVar(OC1RS_NDX);
    sendVar(ADC1BUF0_NDX);

    if (e_state != e_last_state) {
      e_last_state = e_state;
      ASSERT(e_state < MAX_STATE);
      outString(apsz_state[e_state]);
      outString("\n");
    }

    if ( (e_state == MOTOR_OFF_WFP) || (e_state == MOTOR_OFF_WFR) )
      LED = !LED;

    DELAY_MS(100);
    doHeartbeat();
  }
}
