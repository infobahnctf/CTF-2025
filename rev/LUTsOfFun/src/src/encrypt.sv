module encrypt #(
    parameter int KEY_SIZE   = 32,
    parameter int BLOCK_SIZE = 32
)(
    input  logic clk,
    input  logic rst_n,
    input  logic [KEY_SIZE-1:0] key,
    input  logic [BLOCK_SIZE-1:0] plaintext,
    input  logic start,
    output logic [BLOCK_SIZE-1:0] ciphertext,
    output logic done
);
    // ROTL8(plaintext ^ key)
    function automatic [BLOCK_SIZE-1:0] round (
        input logic [BLOCK_SIZE-1:0] s,
        input logic [KEY_SIZE-1:0] k
    );
        logic [BLOCK_SIZE-1:0] tmp;
        tmp = s ^ k;
        return {tmp[BLOCK_SIZE-9:0], tmp[BLOCK_SIZE-1:BLOCK_SIZE-8]};
    endfunction

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ciphertext <= '0;
            done <= 1'b0;
        end else begin
            done <= start;
            if (start) ciphertext <= round(plaintext, key);
        end
    end
endmodule
