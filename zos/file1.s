RDHW1     TITLE 'Hello World for R2 Disasm Test'
RDHW1     AMODE 31
RDHW1     RMODE 24
RDHW1     CSECT
          YREGS
MAIN      DS    0H
          BAKR  R14,0
          LR    R8,R15
          USING MAIN,R8
          LA    R1,MSGOUT
          LA    R0,15
          SVC   93
          XR    R15,R15
          PR
          DS    0F
MSGOUT    DC    CL15'Hello R2 World!'
          DROP  R8
          END
