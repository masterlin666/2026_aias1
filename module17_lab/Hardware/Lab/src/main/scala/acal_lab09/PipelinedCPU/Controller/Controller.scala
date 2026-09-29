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
    // Memory control signal interface
    val IM_Mem_R = Output(Bool())
    val IM_Mem_W = Output(Bool())
    val IM_Length = Output(UInt(4.W))
    val IM_Valid = Input(Bool())

    val DM_Mem_R = Output(Bool())
    val DM_Mem_W = Output(Bool())
    val DM_Length = Output(UInt(4.W))
    val DM_Valid = Input(Bool())

    // branch Comp.
    val E_BrEq = Input(Bool())
    val E_BrLT = Input(Bool())

    // Branch Prediction
    val E_Branch_taken = Output(Bool())
    val E_En = Output(Bool())

    val ID_pc = Input(UInt(memAddrWidth.W))
    val EXE_target_pc = Input(UInt(memAddrWidth.W))

    // Flush
    val Flush_WB_ID_DH = Output(Bool()) 
    val Flush_BH = Output(Bool()) 

    // Stall
    val Stall_WB_ID_DH = Output(Bool()) 
    val Stall_MA = Output(Bool()) 

    // inst
    val IF_Inst = Input(UInt(32.W))
    val ID_Inst = Input(UInt(32.W))
    val EXE_Inst = Input(UInt(32.W))
    val MEM_Inst = Input(UInt(32.W))
    val WB_Inst = Input(UInt(32.W))

    // sel
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
  
  // Inst Decode for each stage
  val IF_opcode = io.IF_Inst(6, 0)
  val ID_opcode = io.ID_Inst(6, 0)

  val EXE_opcode = io.EXE_Inst(6, 0)
  val EXE_funct3 = io.EXE_Inst(14, 12)
  val EXE_funct7 = io.EXE_Inst(31, 25)

  val MEM_opcode = io.MEM_Inst(6, 0)
  val MEM_funct3 = io.MEM_Inst(14, 12)

  val WB_opcode = io.WB_Inst(6, 0)

  // 1. Control signal - Branch/Jump 決策
  // 修正：只要是 BRANCH 或 JUMP (JAL/JALR)，在 EXE 階段都要啟用控制檢查
  val E_En = Wire(Bool())
  E_En := (EXE_opcode === BRANCH || EXE_opcode === JAL || EXE_opcode === JALR)

  // 修正：JAL 和 JALR 是無條件跳轉，只要遇到就必須是 true.B
  val E_Branch_taken = Wire(Bool())
  E_Branch_taken := MuxLookup(EXE_opcode, false.B, Seq(
    BRANCH -> MuxLookup(EXE_funct3, false.B, Seq(
      "b000".U(3.W) -> io.E_BrEq,  // BEQ
      "b001".U(3.W) -> !io.E_BrEq, // BNE (順便補上更穩)
    )),
    JAL  -> true.B,
    JALR -> true.B
  ))

  io.E_En := E_En
  io.E_Branch_taken := E_Branch_taken

  // 2. PC predict miss 判定 (Control Hazard 核心)
  // 當確定要跳轉，且目標位址與順序執行的 PC 不同時，觸發 Predict_Miss
  val Predict_Miss = Wire(Bool())
  Predict_Miss := (E_En && E_Branch_taken)

  // Control signal - PC 選擇
  // 這裡假設你們第一組的位元映射中，1.U 代表 EXE_T_PC，0.U 代表 PC+4 (請依據 pc_sel_map 對齊)
    when(Predict_Miss){
    io.PCSel := 2.U(2.W) // 依據 pc_sel_map.EXE_T_PC，這才是真正的跳轉目標！
  }.otherwise{
    io.PCSel := 0.U(2.W) // IF_PC_PLUS_4
  }

  // 3. Control signal - Branch comparator
  io.E_BrUn := (io.EXE_Inst(13) === 1.U)

  // 4. Control signal - Immediate generator
  io.D_ImmSel := MuxLookup(ID_opcode, 0.U, Seq(
    OP_IMM -> I_type,
    LOAD   -> I_type,
    JALR   -> I_type,
    STORE  -> S_type,
    BRANCH -> B_type,
    LUI    -> U_type,
    AUIPC  -> U_type,
    JAL    -> J_type
  ))

  // 5. Control signal - Scalar ALU
  // 修正：JAL / JALR / BRANCH 都需要計算 PC + Imm 或 PC + 4
  io.E_ASel := MuxLookup(EXE_opcode, 0.U, Seq(
    BRANCH -> 1.U,
    AUIPC  -> 1.U,
    LUI    -> 2.U,
    JAL    -> 1.U, // PC
    JALR   -> 0.U  // rs1
  ))   

  io.E_BSel := MuxLookup(EXE_opcode, 1.U, Seq(
    OP     -> 0.U,
    BRANCH -> 0.U,
    JAL    -> 1.U, // Imm
    JALR   -> 1.U  // Imm
  ))

  val imm_funct7 = Mux(
    EXE_funct3 === "b001".U || EXE_funct3 === "b101".U,
    EXE_funct7,
    0.U(7.W)
  )

  // 修正：遇到 BRANCH / JAL / JALR 時，ALU 內部必須做加法來算地址或做別的事
  io.E_ALUSel := MuxLookup(EXE_opcode, (Cat(0.U(7.W), "b11111".U, 0.U(3.W))), Seq(
    OP     -> (Cat(EXE_funct7, "b11111".U, EXE_funct3)),
    OP_IMM -> (Cat(imm_funct7, "b11111".U, EXE_funct3)),
    BRANCH -> (Cat(0.U(7.W), "b11111".U, "b000".U(3.W))), // ADD
    JAL    -> (Cat(0.U(7.W), "b11111".U, "b000".U(3.W))), // ADD
    JALR   -> (Cat(0.U(7.W), "b11111".U, "b000".U(3.W)))  // ADD
  )) 

  // 6. Control signal - Data Memory
  io.DM_Mem_R := (MEM_opcode === LOAD)
  io.DM_Mem_W := (MEM_opcode === STORE)
  io.DM_Length := Cat(0.U(1.W), MEM_funct3)

  // 7. Control signal - Inst Memory
  io.IM_Mem_R := true.B 
  io.IM_Mem_W := false.B 
  io.IM_Length := "b0010".U 

  // 8. Control signal - Scalar Write Back
  // 完美融合原初版精神：直接解碼 WB_opcode，讓寫回訊號永遠準時
  io.W_RegWEn := MuxLookup(WB_opcode, false.B, Seq(
    OP_IMM -> true.B,
    OP     -> true.B,
    LOAD   -> true.B,
    LUI    -> true.B,
    AUIPC  -> true.B,
    JAL    -> true.B,
    JALR   -> true.B
  ))  

  io.W_WBSel := MuxLookup(WB_opcode, ALUOUT, Seq(
    LOAD -> LD_DATA,
    JAL  -> PC_PLUS_4,
    JALR -> PC_PLUS_4
  ))

  // 9. Others & Hazard Signals
  io.Hcf := (IF_opcode === HCF)

  io.Stall_WB_ID_DH := false.B 
  io.Stall_MA       := false.B 
  io.Flush_WB_ID_DH  := false.B
  
  // 核心融合點：發生 Branch/Jump 跳轉時，必須向外發出 Flush 訊號清洗流水線
  io.Flush_BH       := Predict_Miss
}