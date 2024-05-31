/* verilator lint_off REALCVT */

// FROM General Instruments AY-3-8910 / 8912 Programmable Sound Generator (PSG) data Manual.
// Section 3.7 D/A Converter Operation
// 
// Steps from the diagram: 1V, .707V, .5V, .303V (?), .25V, .1515V (?), .125V .. (not specified) .. 0V


// FROM Yamaha YM2149 Software-Controlled Sound Generator (SSG) data Manual.
// Section 2. D/A Converter
// 
// Steps from the diagram: 1V, .841, .707, .595, .5, .42, .354, .297, .25, .21, .177, .149, .125 .. (not specified) .. 0V

// FROM Yamaha YM2149 Software-Controlled Sound Generator (SSG) data Manual.
// Section 3. DC Characteristics
// Max current per analog channel: 2 mA
// Peak-to-peak voltage swing given 1 kOhm load: 1.35V (min 0.96V)

module amplitude #( parameter CONTROL_BITS = 4, parameter VOLUME_BITS = 15 ) (
    input  wire in,
    input  wire [CONTROL_BITS-1:0] control,
    output reg  [VOLUME_BITS-1:0] pwm_out,
    output reg  [14:0] dac_out
);
    localparam real MAX_VOLUME = (1 << VOLUME_BITS) - 1;
    `define ATLEAST1(i) ($rtoi(i)>1 ? $rtoi(i) : 1)
    always @(*) begin
        case(in ? control : 0)
            15: pwm_out = `ATLEAST1(MAX_VOLUME * 1.0  );
            14: pwm_out = `ATLEAST1(MAX_VOLUME * 0.707);
            13: pwm_out = `ATLEAST1(MAX_VOLUME * 0.5  );
            12: pwm_out = `ATLEAST1(MAX_VOLUME * 0.354);
            11: pwm_out = `ATLEAST1(MAX_VOLUME * 0.25 );
            10: pwm_out = `ATLEAST1(MAX_VOLUME * 0.177);   
            9:  pwm_out = `ATLEAST1(MAX_VOLUME * 0.125);
            8:  pwm_out = `ATLEAST1(MAX_VOLUME * 0.089);
            7:  pwm_out = `ATLEAST1(MAX_VOLUME * 0.063);
            6:  pwm_out = `ATLEAST1(MAX_VOLUME * 0.045);
            5:  pwm_out = `ATLEAST1(MAX_VOLUME * 0.032);
            4:  pwm_out = `ATLEAST1(MAX_VOLUME * 0.023);
            3:  pwm_out = `ATLEAST1(MAX_VOLUME * 0.016);
            2:  pwm_out = `ATLEAST1(MAX_VOLUME * 0.012);
            1:  pwm_out = `ATLEAST1(MAX_VOLUME * 0.008);
            0:  pwm_out =                        0;
        endcase
        `undef ATLEAST1
    end

    always @(*) begin
        case(in ? control : 0)
            15: dac_out = 15'b100_0000_0000_0000;
            14: dac_out = 15'b010_0000_0000_0000;
            13: dac_out = 15'b001_0000_0000_0000;
            12: dac_out = 15'b000_1000_0000_0000;
            11: dac_out = 15'b000_0100_0000_0000;
            10: dac_out = 15'b000_0010_0000_0000;
            9:  dac_out = 15'b000_0001_0000_0000;
            8:  dac_out = 15'b000_0000_1000_0000;
            7:  dac_out = 15'b000_0000_0100_0000;
            6:  dac_out = 15'b000_0000_0010_0000;
            5:  dac_out = 15'b000_0000_0001_0000;
            4:  dac_out = 15'b000_0000_0000_1000;
            3:  dac_out = 15'b000_0000_0000_0100;
            2:  dac_out = 15'b000_0000_0000_0010;
            1:  dac_out = 15'b000_0000_0000_0001;
            0:  dac_out = 15'b000_0000_0000_0000;
        endcase
    end
endmodule

