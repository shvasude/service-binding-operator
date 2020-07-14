package assert

// Assertions provides assertion methods around the
// TestingT interface.
type Assertions struct {
	t TestingT
}

// New makes a new Assertions object for the specified TestingT.
func New(t TestingT) *Assertions {
	return &Assertions{
		t: t,
	}
}

<<<<<<< HEAD
//go:generate sh -c "cd ../_codegen && go build && cd - && ../_codegen/_codegen -output-package=assert -template=assertion_forward.go.tmpl -include-format-funcs"
=======
//go:generate go run ../_codegen/main.go -output-package=assert -template=assertion_forward.go.tmpl -include-format-funcs
>>>>>>> 245092a0fa73e9b71cfe2cc7cf10cc382be32c06
