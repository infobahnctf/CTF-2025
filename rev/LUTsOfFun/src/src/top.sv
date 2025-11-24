module axi_encrypt_slave #(
    parameter int ADDR_W = 5,  // 32B aperture
    parameter int DATA_W = 32
)(
    input  logic                 ACLK,
    input  logic                 ARESETn,

    // AXI4-Lite Write Address Channel
    input  logic [ADDR_W-1:0]    S_AWADDR,
    input  logic                 S_AWVALID,
    output logic                 S_AWREADY,

    // AXI4-Lite Write Data Channel
    input  logic [DATA_W-1:0]     S_WDATA,
    input  logic [(DATA_W/8)-1:0] S_WSTRB,
    input  logic                  S_WVALID,
    output logic                  S_WREADY,

    // AXI4-Lite Write Response Channel
    output logic [1:0]           S_BRESP,
    output logic                 S_BVALID,
    input  logic                 S_BREADY,

    // AXI4-Lite Read Address Channel
    input  logic [ADDR_W-1:0]    S_ARADDR,
    input  logic                 S_ARVALID,
    output logic                 S_ARREADY,

    // AXI4-Lite Read Data Channel
    output logic [DATA_W-1:0]    S_RDATA,
    output logic [1:0]           S_RRESP,
    output logic                 S_RVALID,
    input  logic                 S_RREADY
);

    // -----------------------------
    // Flag ROM (big-endian 32-bit words)
    // ASCII:   infobahn{b1t5tr4mR3vers1ngCanB3 H4rd, bUt somet1mes you don't n33d to reverse everything :0}
    // HEX:     696e666f6261686e7b623174357472346d523376657273316e6743616e423320483472642c2062557420736f6d6574316d657320796f7520646f6e2774206e33336420746f20726576657273652065766572797468696e67203a307d
    // Blocks:  23
    // -----------------------------
    localparam int FLAG_LEN = 23;
    localparam logic [31:0] FLAG_ROM [0:FLAG_LEN-1] = '{
        32'h696e666f, 32'h6261686e, 32'h7b623174, 32'h35747234, 32'h6d523376,
        32'h65727331, 32'h6e674361, 32'h6e423320, 32'h48347264, 32'h2c206255,
        32'h7420736f, 32'h6d657431, 32'h6d657320, 32'h796f7520, 32'h646f6e27,
        32'h74206e33, 32'h33642074, 32'h6f207265, 32'h76657273, 32'h65206576,
        32'h65727974, 32'h68696e67, 32'h203a307d
    };

    // -----------------------------
    // Registers & wires
    // -----------------------------
    localparam logic [4:0] REG_KEY    = 5'h00; // 0x00
    localparam logic [4:0] REG_CTRL   = 5'h04; // 0x04
    localparam logic [4:0] REG_STATUS = 5'h08; // 0x08
    localparam logic [4:0] REG_CTEXT  = 5'h0C; // 0x0C
    localparam logic [4:0] REG_INDEX  = 5'h10; // 0x10
    localparam logic [4:0] REG_LENGTH = 5'h14; // 0x14

    logic [31:0] key_reg, ctext_reg;
    logic [31:0] index_reg;
    logic        done_reg;
    logic        auto_inc;

    logic start_pulse, clr_done;

    // -----------------------------
    // AXI-lite write channel (independent AW/W capture)
    // -----------------------------
    logic [4:0]  wr_addr;
    logic [31:0] wr_data;
    logic [3:0]  wr_strb;
    logic        aw_captured, w_captured;
    logic        wr_index_we;
    logic [31:0] wr_index_val;

    assign S_AWREADY = ARESETn && !aw_captured && !S_BVALID;
    assign S_WREADY  = ARESETn && !w_captured  && !S_BVALID;

    always_ff @(posedge ACLK or negedge ARESETn) begin
        if (!ARESETn) begin
            aw_captured <= 1'b0;
            w_captured  <= 1'b0;
            wr_addr     <= '0;
            wr_data     <= '0;
            wr_strb     <= '0;

            S_BVALID    <= 1'b0;
            S_BRESP     <= 2'b00;

            key_reg     <= 32'h0;
            auto_inc    <= 1'b0;

            start_pulse <= 1'b0;
            clr_done    <= 1'b0;

            wr_index_we  <= 1'b0;
            wr_index_val <= 32'h0;
        end else begin
            // capture AW
            if (S_AWREADY && S_AWVALID) begin
                wr_addr     <= S_AWADDR[4:0];
                aw_captured <= 1'b1;
            end

            // capture W
            if (S_WREADY && S_WVALID) begin
                wr_data     <= S_WDATA;
                wr_strb     <= S_WSTRB;
                w_captured  <= 1'b1;
            end

            // default pulses low
            start_pulse <= 1'b0;
            clr_done    <= 1'b0;
            wr_index_we <= 1'b0;

            // commit write when both beats captured
            if (!S_BVALID && aw_captured && w_captured) begin
                unique case (wr_addr)
                    REG_KEY: begin
                        if (wr_strb[0]) key_reg[7:0]   <= wr_data[7:0];
                        if (wr_strb[1]) key_reg[15:8]  <= wr_data[15:8];
                        if (wr_strb[2]) key_reg[23:16] <= wr_data[23:16];
                        if (wr_strb[3]) key_reg[31:24] <= wr_data[31:24];
                    end
                    REG_INDEX: begin
                        wr_index_we  <= 1'b1;
                        wr_index_val <= (wr_data < FLAG_LEN) ? wr_data : FLAG_LEN; // sentinel for "out of range"
                    end
                    REG_CTRL: begin
                        auto_inc    <= wr_data[2];
                        start_pulse <= wr_data[0];
                        clr_done    <= wr_data[1];
                    end
                    default: ;
                endcase

                S_BVALID    <= 1'b1;
                S_BRESP     <= 2'b00;

                aw_captured <= 1'b0;
                w_captured  <= 1'b0;
            end

            if (S_BVALID && S_BREADY) begin
                S_BVALID <= 1'b0;
            end
        end
    end

    // -----------------------------
    // AXI-lite read channel
    // -----------------------------
    assign S_ARREADY = ARESETn && !S_RVALID;

    always_ff @(posedge ACLK or negedge ARESETn) begin
        if (!ARESETn) begin
            S_RVALID <= 1'b0;
            S_RRESP  <= 2'b00;
            S_RDATA  <= '0;
        end else begin
            if (S_ARREADY && S_ARVALID) begin
                unique case (S_ARADDR[4:0])
                    REG_KEY   : S_RDATA <= key_reg;
                    REG_CTRL  : S_RDATA <= {29'b0, auto_inc, 1'b0, 1'b0};
                    REG_STATUS: S_RDATA <= {31'b0, done_reg};
                    REG_CTEXT : S_RDATA <= ctext_reg;
                    REG_INDEX : S_RDATA <= index_reg;
                    REG_LENGTH: S_RDATA <= FLAG_LEN;
                    default   : S_RDATA <= '0;
                endcase
                S_RRESP  <= 2'b00;
                S_RVALID <= 1'b1;
            end else if (S_RVALID && S_RREADY) begin
                S_RVALID <= 1'b0;
            end
        end
    end

    // -----------------------------
    // DONE + CTEXT latch and datapath
    // -----------------------------
    logic [31:0] core_ctext;
    logic        core_done;

    always_ff @(posedge ACLK or negedge ARESETn) begin
        if (!ARESETn) begin
            done_reg  <= 1'b0;
            ctext_reg <= 32'h0;
        end else begin
            if (clr_done)
                done_reg <= 1'b0;

            if (core_done) begin
                done_reg  <= 1'b1;
                ctext_reg <= core_ctext;
            end
        end
    end

    // -----------------------------
    // index_reg: single owner block
    // -----------------------------
    always_ff @(posedge ACLK or negedge ARESETn) begin
        if (!ARESETn) begin
            index_reg <= 32'h0;
        end else begin
            // AUTO_INC on encryption done
            if (core_done && auto_inc) begin
                if (index_reg == FLAG_LEN-1)
                    index_reg <= '0;
                else
                    index_reg <= index_reg + 1;
            end
            // AXI write to INDEX overrides auto_inc in the same cycle
            if (wr_index_we) begin
                index_reg <= wr_index_val;
            end
        end
    end

    // -----------------------------
    // Datapath select + core
    // -----------------------------
    logic [31:0] plaintext_sel;
    assign plaintext_sel = (index_reg < FLAG_LEN) ? FLAG_ROM[index_reg] : 32'h00000000;

    encrypt #(
        .KEY_SIZE(32),
        .BLOCK_SIZE(32)
    ) u_encrypt (
        .clk        (ACLK),
        .rst_n      (ARESETn),
        .key        (key_reg),
        .plaintext  (plaintext_sel),
        .start      (start_pulse),
        .ciphertext (core_ctext),
        .done       (core_done)
    );

endmodule
