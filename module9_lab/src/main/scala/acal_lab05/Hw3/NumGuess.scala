package acal_lab05.Hw3

import chisel3._
import chisel3.util._

class NumGuess(seed: Int = 1) extends Module {
  require(seed > 0, "Seed cannot be 0")

  val io = IO(new Bundle {
    val gen     = Input(Bool())
    val guess   = Input(UInt(16.W))
    val puzzle  = Output(Vec(4, UInt(4.W)))
    val ready   = Output(Bool())
    val g_valid = Output(Bool()) // 這裡修正為 g_valid
    val A       = Output(UInt(3.W))
    val B       = Output(UInt(3.W))

    // 測試檔需要的輸入
    val s_valid = Input(Bool())
  })

  // 1. 實例化 PRNG
  val prng = Module(new PRNG(seed))
  prng.io.gen := io.gen
  io.puzzle   := prng.io.puzzle

  // 2. 狀態機
  val sIdle :: sWaitGuess :: sResult :: Nil = Enum(3)
  val state = RegInit(sIdle)

  // 3. 解碼 Guess
  val g = Wire(Vec(4, UInt(4.W)))
  g(0) := io.guess(15, 12)
  g(1) := io.guess(11, 8)
  g(2) := io.guess(7, 4)
  g(3) := io.guess(3, 0)

  // 4. A、B 計算 (組合邏輯)
  // 計算 A: 位置對、數字對
  val matchA = for (i <- 0 until 4) yield (prng.io.puzzle(i) === g(i))
  val countA = PopCount(matchA)

  // 計算 B: 數字對、位置錯
  // 因為 PRNG 保證不重複，所以只要 puzzle 裡有出現且不是在同一個位置就是 B
  val matchB = for {
    i <- 0 until 4
    j <- 0 until 4
    if i != j
  } yield (prng.io.puzzle(i) === g(j))
  val countB = PopCount(matchB)

  // 5. 輸出暫存器
  val regA = RegInit(0.U(3.W))
  val regB = RegInit(0.U(3.W))
  val regGValid = RegInit(false.B)

  // 6. 遊戲邏輯控制
  switch(state) {
    is(sIdle) {
      regGValid := false.B
      // 當玩家按下 gen 且 PRNG 完成產生
      when(prng.io.ready) {
        state := sWaitGuess
      }
    }
    is(sWaitGuess) {
      // 在此狀態下，測試檔會偵測 ready 並給出 guess 與 s_valid
      when(io.s_valid) {
        state := sResult
        regA := countA
        regB := countB
        regGValid := true.B
      }
    }
    is(sResult) {
      regGValid := false.B
      when(regA === 4.U) {
        state := sIdle // 贏了，回初始狀態
      }.otherwise {
        state := sWaitGuess // 沒贏，繼續猜
      }
    }
  }

  // 7. 賦值
  io.ready   := (state === sWaitGuess)
  io.g_valid := regGValid
  io.A       := regA
  io.B       := regB
}