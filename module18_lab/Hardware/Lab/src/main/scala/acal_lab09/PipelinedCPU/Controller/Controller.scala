package acal_lab09.PiplinedCPU.Controller

import chisel3._
import chisel3.util._

import acal_lab09.PiplinedCPU.opcode_map._
import acal_lab09.PiplinedCPU.condition._
import acal_lab09.PiplinedCPU.inst_type._
import acal_lab09.PiplinedCPU.alu_op_map._
import acal_lab09.PiplinedCPU.pc_sel_map._
import acal_lab09.PiplinedCPU.wb_sel_map._
import acal_lab09.PiplinedCPU.forwarding_sel_map._

class Controller(memAddrWidth: Int) extends Module {
  val io = IO(new Bundle {
    val IM_Mem_R = Output(Bool())
    val IM_Mem_W = Output(Bool())
    val IM_Length = Output(UInt(4.W))
    val IM_Valid = Input(Bool())

    val DM_Mem_R = Output(Bool())
    val DM_Mem_W = Output(Bool())
    val DM_Length = Output(UInt(4.W))
    val DM_Valid = Input(Bool())

    val E_BrEq = Input(Bool())
    val E_BrLT = Input(Bool())

    val E_Branch_taken = Output(Bool())
    val E_En = Output(Bool())

    val ID_pc = Input(UInt(memAddrWidth.W))
    val EXE_target_pc = Input(UInt(memAddrWidth.W))

    val Flush_WB_ID_DH = Output(Bool()) 
    val Flush_BH = Output(Bool()) 

    val Stall_WB_ID_DH = Output(Bool()) 
    val Stall_MA = Output(Bool()) 

    val IF_Inst = Input(UInt(32.W))
    val ID_Inst = Input(UInt(32.W))
    val EXE_Inst = Input(UInt(32.W))
    val MEM_Inst = Input(UInt(32.W))
    val WB_Inst = Input(UInt(32.W))

    val PCSel = Output(UInt(2.W))
    val D_ImmSel = Output(UInt(3.W))
    val W_RegWEn = Output(Bool())
    val E_BrUn = Output(Bool())
    val E_ASel = Output(UInt(2.W))
    val E_BSel = Output(UInt(1.W))
    val E_ALUSel = Output(UInt(15.W))
    val W_WBSel = Output(UInt(2.W))

    val Hcf = Output(Bool())
  })
  
  val IF_opcode = io.IF_Inst(6, 0)
  val ID_opcode = io.ID_Inst(6, 0)

  val EXE_opcode = io.EXE_Inst(6, 0)
  val EXE_funct3 = io.EXE_Inst(14, 12)
  val EXE_funct7 = io.EXE_Inst(31, 25)

  val MEM_opcode = io.MEM_Inst(6, 0)
  val MEM_funct3 = io.MEM_Inst(14, 12)

  val WB_opcode = io.WB_Inst(6, 0)

  // Control signal - Branch/Jump
  val E_En = Wire(Bool())
  E_En := (EXE_opcode === BRANCH || EXE_opcode === JAL || EXE_opcode === JALR)
  
  val E_Branch_taken = Wire(Bool())
  E_Branch_taken := MuxLookup(EXE_opcode, false.B, Seq(
    JAL    -> true.B,
    JALR   -> true.B,
    BRANCH -> MuxLookup(EXE_funct3, false.B, Seq(
      "b000".U(3.W) -> io.E_BrEq,          // BEQ
      "b001".U(3.W) -> !io.E_BrEq,         // BNE
      "b100".U(3.W) -> io.E_BrLT,          // BLT
      "b101".U(3.W) -> !io.E_BrLT,         // BGE
      "b110".U(3.W) -> io.E_BrLT,          // BLTU
      "b111".U(3.W) -> !io.E_BrLT,         // BGEU
    )),
  ))

  io.E_En := E_En
  io.E_Branch_taken := E_Branch_taken

  // Control Hazard 判定 (Branch Misprediction)
  val Predict_Miss = Wire(Bool())
  Predict_Miss := E_En && E_Branch_taken

  when(Predict_Miss){
    io.PCSel := EXE_T_PC
  }.otherwise{
    io.PCSel := IF_PC_PLUS_4
  }

  io.E_BrUn := (EXE_funct3 === "b110".U || EXE_funct3 === "b111".U)

  io.D_ImmSel := MuxLookup(ID_opcode, 0.U, Seq(
    OP_IMM -> I_type,
    LOAD   -> I_type,
    JALR   -> I_type,
    STORE  -> S_type,
    BRANCH -> B_type,
    LUI    -> U_type,
    AUIPC  -> U_type,
    JAL    -> J_type,
  )) 

  io.E_ASel := MuxLookup(EXE_opcode, 0.U, Seq(
    BRANCH -> 1.U,
    JAL    -> 1.U,
    AUIPC  -> 1.U,
    LUI    -> 2.U,
    JALR   -> 0.U,
  ))    
  io.E_BSel := MuxLookup(EXE_opcode, 0.U, Seq(
    OP     -> 0.U, 
    OP_IMM -> 1.U, 
    LOAD   -> 1.U,
    STORE  -> 1.U,
    BRANCH -> 1.U,
    LUI    -> 1.U,
    AUIPC  -> 1.U,
    JAL    -> 1.U,
    JALR   -> 1.U,
  ))

  // ALU 解碼
  val ALU_ADD_SIGNAL = Cat(0.U(7.W), "b11111".U, "b000".U(3.W))

  io.E_ALUSel := MuxLookup(EXE_opcode, (Cat(0.U(7.W), "b11111".U, 0.U(3.W))), Seq(
    OP     -> (Cat(EXE_funct7, "b11111".U, EXE_funct3)),
    OP_IMM -> (Cat(Mux(EXE_funct3 === "b101".U, EXE_funct7, 0.U(7.W)), "b11111".U, EXE_funct3)),
    LOAD   -> ALU_ADD_SIGNAL, 
    STORE  -> ALU_ADD_SIGNAL, 
    BRANCH -> ALU_ADD_SIGNAL, // 【核心修正】讓 BRANCH 指令在 EXE 級時，叫 ALU 執行加法 (PC + Imm)
    JAL    -> ALU_ADD_SIGNAL, // 【核心修正】讓 JAL 指令也執行加法 (PC + Imm)
    JALR   -> ALU_ADD_SIGNAL, // 【核心修正】讓 JALR 指令也執行加法 (rs1 + Imm)
    AUIPC  -> ALU_ADD_SIGNAL, 
  ))

  io.DM_Mem_R := (MEM_opcode === LOAD)
  io.DM_Mem_W := (MEM_opcode === STORE)
  io.DM_Length := Cat(0.U(1.W), MEM_funct3)

  io.IM_Mem_R := true.B 
  io.IM_Mem_W := false.B 
  io.IM_Length := "b0010".U 

  io.W_RegWEn := MuxLookup(WB_opcode, false.B, Seq(
    OP     -> true.B,
    OP_IMM -> true.B,
    AUIPC  -> true.B,
    LUI    -> true.B,
    JAL    -> true.B,
    JALR   -> true.B,
    LOAD   -> true.B,
  ))  

  io.W_WBSel := MuxLookup(WB_opcode, ALUOUT, Seq(
    OP     -> ALUOUT,
    OP_IMM -> ALUOUT,
    LUI    -> ALUOUT,
    AUIPC  -> ALUOUT,
    LOAD   -> LD_DATA,
    JAL    -> PC_PLUS_4, 
    JALR   -> PC_PLUS_4,
  )) 

  // Hcf should only assert when the halt instruction reaches the WB stage.
  // This ensures earlier instructions in-flight have committed before the testbench exits.
  io.Hcf := (WB_opcode === HCF)

  /****************** Data Hazard 偵測邏輯 (嚴格安全版) ******************/
val ID_rs1 = io.ID_Inst(19, 15)
  val ID_rs2 = io.ID_Inst(24, 20)
  
  // 核心修正：我們必須精準追蹤前面各級正在流動的暫存器 rd 目的地
  val EXE_rd = io.EXE_Inst(11, 7)
  val MEM_rd = io.MEM_Inst(11, 7)
  val WB_rd  = io.WB_Inst(11, 7)

  // 1. 檢查 ID 階段指令是否需要讀取 rs1 / rs2
  val is_D_use_rs1 = MuxLookup(ID_opcode, false.B, Seq(
    OP     -> true.B,
    OP_IMM -> true.B,
    BRANCH -> true.B,
    JALR   -> true.B,
    LOAD   -> true.B,
    STORE  -> true.B,
  )) && (ID_rs1 =/= 0.U)

  val is_D_use_rs2 = MuxLookup(ID_opcode, false.B, Seq(
    OP     -> true.B,
    BRANCH -> true.B,
    STORE  -> true.B,
  )) && (ID_rs2 =/= 0.U)

  // 2. 檢查前面各級指令是否擁有寫回 rd 的能力
  // 修正重點：直接解碼各級暫存器裡的 Opcode，確認它們會改寫暫存器
  val EXE_writes_rf = MuxLookup(EXE_opcode, false.B, Seq(
    OP -> true.B, OP_IMM -> true.B, AUIPC -> true.B, LUI -> true.B, JAL -> true.B, JALR -> true.B, LOAD -> true.B
  )) && (EXE_rd =/= 0.U)

  val MEM_writes_rf = MuxLookup(MEM_opcode, false.B, Seq(
    OP -> true.B, OP_IMM -> true.B, AUIPC -> true.B, LUI -> true.B, JAL -> true.B, JALR -> true.B, LOAD -> true.B
  )) && (MEM_rd =/= 0.U)

  val WB_writes_rf  = MuxLookup(WB_opcode, false.B, Seq(
    OP -> true.B, OP_IMM -> true.B, AUIPC -> true.B, LUI -> true.B, JAL -> true.B, JALR -> true.B, LOAD -> true.B
  )) && (WB_rd =/= 0.U)

  // 3. Overlap 嚴格匹配：只要前面任一級會寫入我現在要讀的暫存器，就觸發 Stall！
  val is_D_rs1_EXE_overlap = is_D_use_rs1 && EXE_writes_rf && (ID_rs1 === EXE_rd)
  val is_D_rs2_EXE_overlap = is_D_use_rs2 && EXE_writes_rf && (ID_rs2 === EXE_rd)
  
  val is_D_rs1_MEM_overlap = is_D_use_rs1 && MEM_writes_rf && (ID_rs1 === MEM_rd)
  val is_D_rs2_MEM_overlap = is_D_use_rs2 && MEM_writes_rf && (ID_rs2 === MEM_rd)
  
  val is_D_rs1_WB_overlap  = is_D_use_rs1 && WB_writes_rf  && (ID_rs1 === WB_rd)
  val is_D_rs2_WB_overlap  = is_D_use_rs2 && WB_writes_rf  && (ID_rs2 === WB_rd)

  val is_D_data_hazard = is_D_rs1_EXE_overlap || is_D_rs2_EXE_overlap ||
                         is_D_rs1_MEM_overlap || is_D_rs2_MEM_overlap ||
                         is_D_rs1_WB_overlap  || is_D_rs2_WB_overlap
  /****************** Pipeline Hazard Control ******************/
  
  // 安全鎖：確保 Predict_Miss 只有在真正的分支指令時才有效
  val safe_Predict_Miss = Predict_Miss && (EXE_opcode === BRANCH || EXE_opcode === JAL || EXE_opcode === JALR)
  val dh_stall = is_D_data_hazard && !safe_Predict_Miss
  
  io.Stall_WB_ID_DH := dh_stall
  io.Stall_MA        := false.B 
  
  io.Flush_WB_ID_DH := dh_stall || safe_Predict_Miss
  io.Flush_BH        := safe_Predict_Miss

  // 修正 io.PCSel 的判定，使用安全版的分支預測
  when(safe_Predict_Miss){
    io.PCSel := EXE_T_PC
  }.otherwise{
    io.PCSel := IF_PC_PLUS_4
  }

  /****************** 核心修正：精準控制波形壓制 ******************/
  // 當發生 Data Hazard 導致 ID 階段需要原地 Stall 時，
  // 為了防止流入 EXE 級的氣泡(Bubble)產生惡意寫入，在當前週期壓制輸出。
  io.W_RegWEn := MuxLookup(WB_opcode, false.B, Seq(
    OP     -> true.B,
    OP_IMM -> true.B,
    AUIPC  -> true.B,
    LUI    -> true.B,
    JAL    -> true.B,
    JALR   -> true.B,
    LOAD   -> true.B,
  ))  
  io.DM_Mem_R := (MEM_opcode === LOAD)
  io.DM_Mem_W := (MEM_opcode === STORE)
}
