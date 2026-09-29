package acal_lab05.Hw1

import chisel3._
import chisel3.util._

class TrafficLight_p(Ytime: Int, Gtime: Int, Ptime: Int) extends Module {
  val io = IO(new Bundle {
    val P_button  = Input(Bool())
    val H_traffic = Output(UInt(2.W))  // Off:0 Red:1 Yellow:2 Green:3
    val V_traffic = Output(UInt(2.W))
    val P_traffic = Output(UInt(2.W))  // 行人號誌 0:Off, 1:Red, 3:Green (假設)
    val timer     = Output(UInt(5.W))
  })

  // 定義狀態碼
  val sIdle :: sHGVR :: sHYVR :: sHRVG :: sHRVY :: sPG :: Nil = Enum(6)

  // 狀態與計數暫存器
  val state     = RegInit(sIdle)
  val lastState = RegInit(sIdle) // 用於記錄中斷前的狀態
  val counter   = RegInit(0.U(5.W))

  // 常數定義
  val Off = 0.U; val Red = 1.U; val Yellow = 2.U; val Green = 3.U

  // FSM 邏輯
  when(io.P_button && state =/= sPG) {
    // 中斷發生：記錄當前狀態，跳轉至行人狀態，重置計數
    lastState := state
    state     := sPG
    counter   := (Ptime - 1).U
  } .otherwise {
    when(counter === 0.U) {
      switch(state) {
        is(sIdle) {
          state   := sHGVR
          counter := (Gtime - 1).U
        }
        is(sHGVR) {
          state   := sHYVR
          counter := (Ytime - 1).U
        }
        is(sHYVR) {
          state   := sHRVG
          counter := (Gtime - 1).U
        }
        is(sHRVG) {
          state   := sHRVY
          counter := (Ytime - 1).U
        }
        is(sHRVY) {
          state   := sPG
          counter := (Ptime - 1).U
        }
        is(sPG) {
          // 行人結束，判斷是正常循環還是中斷返回
          val nextState = Mux(lastState === sIdle, sHGVR, lastState)
          state     := nextState
          lastState := sIdle // 清除紀錄
          
          // 重新載入對應狀態的時間
          counter := MuxLookup(nextState, (Gtime - 1).U, Seq(
            sHGVR -> (Gtime - 1).U,
            sHYVR -> (Ytime - 1).U,
            sHRVG -> (Gtime - 1).U,
            sHRVY -> (Ytime - 1).U
          ))
        }
      }
    } .otherwise {
      counter := counter - 1.U
    }
  }

  // 輸出解碼
  io.timer := counter
  
  // 預設輸出
  io.H_traffic := Red
  io.V_traffic := Red
  io.P_traffic := Red

  switch(state) {
    is(sHGVR) { io.H_traffic := Green;  io.V_traffic := Red;   io.P_traffic := Red }
    is(sHYVR) { io.H_traffic := Yellow; io.V_traffic := Red;   io.P_traffic := Red }
    is(sHRVG) { io.H_traffic := Red;    io.V_traffic := Green; io.P_traffic := Red }
    is(sHRVY) { io.H_traffic := Red;    io.V_traffic := Yellow;io.P_traffic := Red }
    is(sPG)   { io.H_traffic := Red;    io.V_traffic := Red;   io.P_traffic := Green }
    is(sIdle) { io.H_traffic := Off;    io.V_traffic := Off;   io.P_traffic := Off }
  }
}