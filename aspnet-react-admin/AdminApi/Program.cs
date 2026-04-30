using System.Collections.Concurrent;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(p => p
        .WithOrigins("http://localhost:5173")
        .AllowAnyHeader()
        .AllowAnyMethod());
});

builder.Services.AddSingleton<UserStore>();

var app = builder.Build();

app.UseSwagger();
app.UseSwaggerUI();
app.UseCors();

const string AdminToken = "demo-admin-token";

app.MapPost("/api/auth/login", (LoginRequest req) =>
{
    if (req.Username == "admin" && req.Password == "admin123")
        return Results.Ok(new { token = AdminToken, username = req.Username, role = "admin" });
    return Results.Unauthorized();
});

bool IsAuthorized(HttpContext ctx)
{
    var auth = ctx.Request.Headers.Authorization.ToString();
    return auth == $"Bearer {AdminToken}";
}

var users = app.MapGroup("/api/users");

users.MapGet("/", (HttpContext ctx, UserStore store) =>
    IsAuthorized(ctx) ? Results.Ok(store.All()) : Results.Unauthorized());

users.MapGet("/{id:int}", (HttpContext ctx, int id, UserStore store) =>
{
    if (!IsAuthorized(ctx)) return Results.Unauthorized();
    var u = store.Get(id);
    return u is null ? Results.NotFound() : Results.Ok(u);
});

users.MapPost("/", (HttpContext ctx, UserInput input, UserStore store) =>
{
    if (!IsAuthorized(ctx)) return Results.Unauthorized();
    if (string.IsNullOrWhiteSpace(input.Name) || string.IsNullOrWhiteSpace(input.Email))
        return Results.BadRequest(new { error = "Name and email are required" });
    var u = store.Add(input);
    return Results.Created($"/api/users/{u.Id}", u);
});

users.MapPut("/{id:int}", (HttpContext ctx, int id, UserInput input, UserStore store) =>
{
    if (!IsAuthorized(ctx)) return Results.Unauthorized();
    var u = store.Update(id, input);
    return u is null ? Results.NotFound() : Results.Ok(u);
});

users.MapDelete("/{id:int}", (HttpContext ctx, int id, UserStore store) =>
{
    if (!IsAuthorized(ctx)) return Results.Unauthorized();
    return store.Delete(id) ? Results.NoContent() : Results.NotFound();
});

app.MapGet("/api/stats", (HttpContext ctx, UserStore store) =>
{
    if (!IsAuthorized(ctx)) return Results.Unauthorized();
    var all = store.All();
    return Results.Ok(new
    {
        totalUsers = all.Count,
        activeUsers = all.Count(u => u.Active),
        adminUsers = all.Count(u => u.Role == "admin")
    });
});

app.MapGet("/", () => Results.Redirect("/swagger"));

app.Run();

public record LoginRequest(string Username, string Password);
public record UserInput(string Name, string Email, string Role, bool Active);
public record User(int Id, string Name, string Email, string Role, bool Active, DateTime CreatedAt);

public class UserStore
{
    private readonly ConcurrentDictionary<int, User> _users = new();
    private int _nextId;

    public UserStore()
    {
        Add(new UserInput("Anthony Yamada", "anthony@example.com", "admin", true));
        Add(new UserInput("Sakura Tanaka", "sakura@example.com", "editor", true));
        Add(new UserInput("Kenji Sato", "kenji@example.com", "viewer", false));
    }

    public List<User> All() => _users.Values.OrderBy(u => u.Id).ToList();
    public User? Get(int id) => _users.TryGetValue(id, out var u) ? u : null;

    public User Add(UserInput input)
    {
        var id = Interlocked.Increment(ref _nextId);
        var u = new User(id, input.Name, input.Email, input.Role ?? "viewer", input.Active, DateTime.UtcNow);
        _users[id] = u;
        return u;
    }

    public User? Update(int id, UserInput input)
    {
        if (!_users.TryGetValue(id, out var existing)) return null;
        var updated = existing with
        {
            Name = input.Name,
            Email = input.Email,
            Role = input.Role ?? existing.Role,
            Active = input.Active
        };
        _users[id] = updated;
        return updated;
    }

    public bool Delete(int id) => _users.TryRemove(id, out _);
}
