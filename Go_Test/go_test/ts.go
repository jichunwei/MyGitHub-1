package main

import (
    "encoding/csv"
    "fmt"
    "io"
    "os"
)

func main() {
    file, err := os.Open("D:\\JTMM.txt")
    if err != nil {
        fmt.Println("Error:", err)
        return
    }
    defer file.Close()
    reader := csv.NewReader(file)
    for {
        record, err := reader.Read()
        if err == io.EOF {
            break
        } else if err != nil {
            fmt.Println("Error:", err)
            return
        }

        fmt.Println(record) // record has the type []string
    }
}

