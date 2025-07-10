  	`define PLAINTEXT 3
  	`define KEY 100
    `define DUMPFILE "3.vcd"

`timescale 1ns/1ps

module tb_unmasked_aes_sbox;
    reg [7:0] in, k;
    wire [7:0] out;

    unmasked_aes_sbox dut(in^k,out);

    initial begin 
    $dumpfile(`DUMPFILE);
    $dumpvars(0, tb_unmasked_aes_sbox);
    $finish;
    end

    initial begin   
  	k=`KEY;
  	in=`PLAINTEXT;
    end

endmodule
