int INPUT_PIN = 2;

long HEADER = 43;

long UP =     22323222;
long DOWN =   23332232; 
long LEFT =   23323232;
long RIGHT =  23323322;

long UP_RIGHT = 23222322;
long UP_LEFT = 23222232;
long DOWN_LEFT = 23332322;
long DOWN_RIGHT = 32232332; 

long RELEASE = 23322332;


long duration(long t1, long t2) { //returns the microseconds between t1 and t2, accounting for overflow
  if (t1 < t2) {
    return t2 - t1;
  }
  return (2147483647 - t1) + t2;
}

class IR_Data { //Represents a sequence of information from the IR reciever
  private:

  int input_pin;
  
  int time_to_num_of_bits(long t) { //returns the number of bits contained in t microseconds
    if (t < 300) {
      return 1;
    } else if (t < 510) {
      return 2;
    } else if (t < 750) {
      return 3;
    } else if (t < 1100) {
      return 4;
    }
    return 5; //should never recieve more than 4 bits
  }

  void reset() { //empties all the data from this IR_Data object
    len = 0;
    data = 0;
  }

  long wait_for_bit_change() { //wait until the ir reciever sends a new bit, returns the time
    int current_bit = digitalRead(input_pin);
    while (digitalRead(input_pin) == current_bit){}
    return micros();
  }

  bool add_bits(long t1, long t2, bool bit_type) { //counts how many bits there are between t1 and t2 then adds those bits to the ir data
    bool success;
    long delta_time = duration(t1, t2);
    int num_new_bits = time_to_num_of_bits(delta_time);
    if (bit_type == 1) {
      success = (num_new_bits == 1); //can only ever recieve one 1
    } else {
      data = data*10 + num_new_bits; //add another digit to data
      len += 1;
      success = (num_new_bits < 5); //can't get more than 5 zeros
    }
    return success;
  }

  public:
  
  long data; //the data from the ir reciever
  int len; //length of the data

  IR_Data(int input) {
    input_pin = input;
    reset();
  }

  bool get_data(int digits) {
    reset();
    long last_time = wait_for_bit_change(); //wait for beginning of start bit
    bool next_bit = (bool) digitalRead(input_pin); //this should always be a 1, but just in case lets do a read
    while (len < digits) {
      long current_time = wait_for_bit_change(); //(it takes < 10 microseconds to get back to this line once a bit change is detected. Good time!)
      bool success = add_bits(last_time, current_time, next_bit);
      if (!success) { //return false if something went wrong
        return false;
      }
      last_time = current_time;
      next_bit = !next_bit; //next bit just keeps flipping
    }
    return true;
  }
  
  void wait_for_silence() { //waits for 3 milliseconds of no ir data
    long start = micros();
    while (micros() < start + 3000) {
      if (digitalRead(input_pin) == 1) { //restart the waiting if any data comes through
        start = micros();
      }
    }
  }
};


IR_Data IRR(INPUT_PIN);

void setup() {
  pinMode(INPUT_PIN, INPUT);
  Serial.begin(9600);
  IRR.wait_for_silence();
}


void send_press(long data) { //(takes ~30 microseconds now that I added the extra stuff... not great but I wait for silence after this so it doesn't matter)
  if (data == UP || data == UP_RIGHT || data == UP_LEFT) {
    Serial.print('u');
  } if (data == DOWN || data == DOWN_RIGHT || data == DOWN_LEFT) {
    Serial.print('d');
  } if (data == LEFT || data == DOWN_LEFT || data == UP_LEFT) {
    Serial.print('l');
  } if (data == RIGHT || data == DOWN_RIGHT || data == UP_RIGHT) {
    Serial.print('r');
  } if (data == RELEASE) {
    Serial.print('^');
  }
}

void loop() {
  bool success = IRR.get_data(2); //(after this line it takes ~12 microseconds to check success && headers, reset data and start looking for a bit change agian. Good time!)
  if (success && IRR.data == HEADER) {
    success = IRR.get_data(8);
    if (success) {
      send_press(IRR.data);
    }
  }
  IRR.wait_for_silence();
}
